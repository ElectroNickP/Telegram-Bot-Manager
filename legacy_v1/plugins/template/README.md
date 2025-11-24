# Plugin Template

Copy this folder to create new plugins quickly!

## 📦 How to Use

### 1. Copy Template
```bash
cp -r plugins/template plugins/my_new_plugin
cd plugins/my_new_plugin
```

### 2. Edit `plugin.py`
```python
class Plugin:
    def __init__(self):
        self.name = "my_new_plugin"  # Change this!
        self.enabled = False
    
    async def handle(self, message, context=""):
        # Your logic here
        if "my keyword" in message.text:
            await message.answer("Handling!")
            return False  # Stop other plugins
        return None  # Pass to next plugin
```

### 3. Edit `config.json`
```json
{
  "enabled": true,
  "name": "my_new_plugin",
  "settings": {
    "api_key": "your_key_here"
  }
}
```

### 4. Restart Bot
```bash
python3 src/core/manager.py
```

Done! Your plugin will auto-load.

## 📋 Plugin Structure

```
plugins/my_plugin/
├── __init__.py       # Import Plugin class
├── plugin.py         # Main plugin code
├── config.json       # Configuration
└── README.md         # Documentation (optional)
```

## 🔧 Plugin Methods

### Required
- `__init__()` - Initialize plugin
- `init()` - Setup resources
- `load_config(config)` - Load configuration
- `handle(message, context)` - Process messages

### Optional
- `on_start()` - Called when bot starts
- `on_stop()` - Called when bot stops
- `get_help()` - Return help text

## 💡 Examples

### Simple Command Plugin
```python
async def handle(self, message, context=""):
    if message.text == "/hello":
        await message.answer("Hello, World!")
        return False
    return None
```

### Keyword Trigger
```python
async def handle(self, message, context=""):
    if "погода" in message.text.lower():
        weather = await self.get_weather()
        await message.answer(f"Погода: {weather}")
        return True
    return None
```

### Always Process
```python
async def handle(self, message, context=""):
    # Log all messages
    logger.info(f"Message: {message.text}")
    return None  # Let other plugins process too
```

## 🚫 Disabling Plugin

Set in `config.json`:
```json
{
  "enabled": false
}
```

Or remove from `config.yaml` active plugins list.

## 🔄 Return Values

- `None` - Plugin didn't handle, continue to next
- `True` - Plugin handled, continue to next
- `False` - Plugin handled, STOP propagation

## 📚 Available Utilities

```python
from src.core.logger import get_logger
from src.core.context import Context

logger = get_logger(__name__)
logger.info(f"[{self.name}] Message received")
```

## 🧪 Testing

```bash
# Test your plugin
python3 -c "
from plugins.my_plugin.plugin import Plugin
p = Plugin()
p.init()
p.load_config({'enabled': True})
print('Plugin loaded successfully!')
"
```

## ✅ Checklist

- [ ] Copied template folder
- [ ] Changed `self.name` in plugin.py
- [ ] Implemented `handle()` logic
- [ ] Enabled in config.json
- [ ] Tested with real message
- [ ] Added to config.yaml active list

Happy coding! 🚀


