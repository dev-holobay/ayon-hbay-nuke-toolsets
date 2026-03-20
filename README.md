# AYON HBAY Nuke Toolsets

AYON addon providing shared toolsets functionality for Nuke. Allows artists to publish and share Nuke toolsets across projects with centralized storage.

## Features

- **Shared Toolsets**: Create and share Nuke toolsets across your team
- **Project-Based Organization**: Organize toolsets by project with configurable storage locations
- **Easy Publishing**: Simple UI panel to publish selected nodes as toolsets
- **Automatic Menu Integration**: Toolsets automatically appear in Nuke's menu
- **Delete Mode**: Optional toolset management and deletion capabilities

## Structure

```
ayon-hbay-nuke-toolsets/
├── server/                    # Server-side addon code
│   ├── __init__.py           # Server addon implementation
│   └── settings.py           # Settings schema
├── client/                    # Client-side code
│   └── hbay_nuke_toolsets/
│       ├── __init__.py       # Client addon entry point
│       ├── addon.py          # Addon implementation
│       ├── api/              # Core API
│       │   ├── lib.py        # Utility functions
│       │   └── toolsets.py   # Toolset management
│       ├── startup/          # Nuke startup scripts
│       │   ├── init.py       # Initial setup
│       │   └── menu.py       # Menu integration
│       └── plugins/          # Pipeline plugins
├── package.py                # Addon metadata
├── version.py               # Version info
└── create_package.py        # Package builder
```

## Installation

1. Build the addon package:
   ```bash
   python create_package.py
   ```

2. Upload the package to your AYON server through the AYON web interface

3. Enable the addon in your AYON bundle

## Configuration

Configure the addon in AYON Studio Settings:

- **Server Prefix**: Network path prefix (e.g., `//server01`)
- **Project Sources**: List of projects with their toolset storage paths
- **Local Toolsets Path**: Optional local studio-wide toolsets location
- **Enable Delete Mode**: Allow users to delete toolsets from the menu

## Usage

### Creating a Toolset

1. Select nodes in Nuke
2. Open **Nodes → sharedToolSets → Create**
3. Choose location and name
4. Click Create

### Loading a Toolset

1. Open **Nodes → sharedToolSets**
2. Navigate to your toolset
3. Click to load into your scene

### Refreshing the Menu

If toolsets don't appear, use **Nodes → sharedToolSets → Refresh**
