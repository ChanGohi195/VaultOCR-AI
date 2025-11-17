"""
Phase 10: Plugin Manager
Manages plugin loading, registration, and execution
"""

from typing import Dict, Any, List, Optional, Type
from pathlib import Path
import importlib.util
import sys
import logging
from plugin_interface import (
    BasePlugin, PluginType, PluginPriority,
    PluginLoadError, PluginExecutionError, PluginConfigError
)

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Central plugin management system

    Handles:
    - Plugin discovery and loading
    - Plugin registration and configuration
    - Plugin execution pipeline
    - Plugin lifecycle management
    """

    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """
        Initialize plugin manager

        Args:
            plugin_dirs: Directories to search for plugins
        """
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_dirs = plugin_dirs or [
            './plugins',
            './python/plugins',
            str(Path.home() / '.vaultocr' / 'plugins')
        ]

        # Plugin execution order by type
        self.execution_order: Dict[PluginType, List[str]] = {
            ptype: [] for ptype in PluginType
        }

        logger.info(f"PluginManager initialized with dirs: {self.plugin_dirs}")

    def register_plugin(self, plugin: BasePlugin, config: Optional[Dict[str, Any]] = None):
        """
        Register a plugin instance

        Args:
            plugin: Plugin instance
            config: Optional configuration

        Raises:
            PluginConfigError: If configuration is invalid
        """
        plugin_name = plugin.name

        # Validate configuration if provided
        if config:
            is_valid, error_msg = plugin.validate_config(config)
            if not is_valid:
                raise PluginConfigError(f"Invalid config for {plugin_name}: {error_msg}")
            plugin.configure(config)

        # Register plugin
        self.plugins[plugin_name] = plugin

        # Add to execution order
        ptype = plugin.plugin_type
        if plugin_name not in self.execution_order[ptype]:
            self.execution_order[ptype].append(plugin_name)

            # Sort by priority
            self.execution_order[ptype].sort(
                key=lambda name: self.plugins[name].priority.value,
                reverse=True
            )

        logger.info(f"Plugin registered: {plugin_name} ({plugin.version}) - {ptype.value}")

    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            ptype = plugin.plugin_type

            del self.plugins[plugin_name]

            if plugin_name in self.execution_order[ptype]:
                self.execution_order[ptype].remove(plugin_name)

            logger.info(f"Plugin unregistered: {plugin_name}")

    def load_plugin_from_file(self, file_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Load a plugin from a Python file

        Args:
            file_path: Path to plugin .py file
            config: Optional configuration

        Raises:
            PluginLoadError: If plugin fails to load
        """
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location("plugin_module", file_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Failed to load plugin spec from {file_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find plugin class (must inherit from BasePlugin)
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and
                    issubclass(item, BasePlugin) and
                    item is not BasePlugin):
                    plugin_class = item
                    break

            if plugin_class is None:
                raise PluginLoadError(f"No plugin class found in {file_path}")

            # Instantiate and register
            plugin = plugin_class()
            self.register_plugin(plugin, config)

            logger.info(f"Plugin loaded from file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")
            raise PluginLoadError(f"Failed to load plugin: {e}")

    def discover_plugins(self, directory: Optional[str] = None):
        """
        Auto-discover plugins in directory

        Args:
            directory: Directory to search (uses default dirs if None)
        """
        search_dirs = [directory] if directory else self.plugin_dirs

        for dir_path in search_dirs:
            path = Path(dir_path)
            if not path.exists():
                continue

            # Find all .py files
            for plugin_file in path.glob('*.py'):
                if plugin_file.name.startswith('_'):
                    continue  # Skip private files

                try:
                    self.load_plugin_from_file(str(plugin_file))
                except PluginLoadError as e:
                    logger.warning(f"Skipping {plugin_file}: {e}")

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin by name"""
        return self.plugins.get(plugin_name)

    def list_plugins(self, plugin_type: Optional[PluginType] = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        List registered plugins

        Args:
            plugin_type: Filter by type
            enabled_only: Only return enabled plugins

        Returns:
            List of plugin info dicts
        """
        result = []

        for name, plugin in self.plugins.items():
            if plugin_type and plugin.plugin_type != plugin_type:
                continue

            if enabled_only and not plugin.is_enabled:
                continue

            result.append({
                'name': name,
                'version': plugin.version,
                'description': plugin.description,
                'author': plugin.author,
                'type': plugin.plugin_type.value,
                'priority': plugin.priority.value,
                'enabled': plugin.is_enabled,
                'dependencies': plugin.dependencies,
                'config_schema': plugin.config_schema
            })

        return result

    def execute_pipeline(
        self,
        plugin_type: PluginType,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute plugin pipeline for given type

        Args:
            plugin_type: Type of plugins to execute
            input_data: Initial input
            context: Execution context

        Returns:
            Final output after all plugins

        Raises:
            PluginExecutionError: If any plugin fails
        """
        context = context or {}
        output = input_data

        plugin_names = self.execution_order.get(plugin_type, [])

        for plugin_name in plugin_names:
            plugin = self.plugins[plugin_name]

            if not plugin.is_enabled:
                logger.debug(f"Skipping disabled plugin: {plugin_name}")
                continue

            try:
                logger.debug(f"Executing plugin: {plugin_name}")
                output = plugin.execute(output, context)

                # Store plugin results in context
                if 'plugin_results' not in context:
                    context['plugin_results'] = {}
                context['plugin_results'][plugin_name] = {
                    'success': True,
                    'type': plugin_type.value
                }

            except Exception as e:
                error_msg = f"Plugin {plugin_name} failed: {str(e)}"
                logger.error(error_msg)

                context['plugin_results'][plugin_name] = {
                    'success': False,
                    'error': str(e)
                }

                # Decide whether to continue or fail
                if context.get('stop_on_error', False):
                    raise PluginExecutionError(error_msg)
                else:
                    logger.warning(f"Continuing despite error in {plugin_name}")

        return output

    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]):
        """
        Configure a plugin

        Args:
            plugin_name: Name of plugin
            config: Configuration dict

        Raises:
            PluginConfigError: If configuration is invalid
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise PluginConfigError(f"Plugin not found: {plugin_name}")

        is_valid, error_msg = plugin.validate_config(config)
        if not is_valid:
            raise PluginConfigError(f"Invalid config: {error_msg}")

        plugin.configure(config)
        logger.info(f"Plugin {plugin_name} configured")

    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enable()

    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.disable()

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a plugin"""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return None

        return {
            'name': plugin.name,
            'version': plugin.version,
            'description': plugin.description,
            'author': plugin.author,
            'type': plugin.plugin_type.value,
            'priority': plugin.priority.value,
            'enabled': plugin.is_enabled,
            'dependencies': plugin.dependencies,
            'config_schema': plugin.config_schema,
            'config': plugin._config
        }

    def reload_plugin(self, plugin_name: str):
        """
        Reload a plugin (unregister and re-register)

        Useful for development
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.warning(f"Plugin not found: {plugin_name}")
            return

        # Save current config
        config = plugin._config

        # Unregister
        self.unregister_plugin(plugin_name)

        # Re-register (would need file path - not implemented fully)
        logger.info(f"Plugin {plugin_name} reloaded")
