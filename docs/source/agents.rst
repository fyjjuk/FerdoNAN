Agents Module
=============

Built-in Agents
---------------

Buscador Web (buscador_web)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Web search specialist using DuckDuckGo.

Experto Linux (experto_linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Linux Fedora system administration expert.

Narrador D&D (narrador_dnd)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dungeons & Dragons narrative generator.

Spotify Player (spotify_player)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Spotify playback controller.

Dev Assistant (dev_assistant)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Software development assistant with GitHub integration.

Creating New Agents
-------------------

1. Create directory: ``agents/my_agent/``
2. Create ``config.yaml`` with agent configuration
3. Create YAML routes in ``routes/`` directory
4. Restart FerdoNAN to detect the new agent

Route Structure
---------------

.. code-block:: yaml

   route_id: "my_route"
   type: "cognitive"  # or "script"
   description: "keywords, for, routing"
   system_prompt: "You are a helpful assistant..."
   tools_allowed:
     - native:my_tool
   gatekeeper_required: false
