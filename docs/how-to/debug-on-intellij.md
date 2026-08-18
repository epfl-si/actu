# How to debug in Intellij

- Install the lsp4ij plugins
- Assert your server is started with "-m debugpy --listen 0.0.0.0:5678"
  - it should be the case for this project
- In Intellij, add a new debug configuration
  - select "attach to DAP"
  - set a name, ex. "Attach to the actu server"
  - set "Remote address" to "127.0.0.1:5678"
- Run the newly configured debug configuration by clicking the little green bug
- Go into the code, set your breakpoint where you need it
  - if your debugger is correctly linked, you should see a checkmark on the breakpoint

Now you can browse the app and see the debugger being triggered.
