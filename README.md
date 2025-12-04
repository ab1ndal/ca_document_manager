To run the dev mode, execute the following:

```
poetry run python dev_launcher.py
```

To create the exe file:

Build the npm modules

```
cd frontend
npm run build
```

Create the exec:

```
poetry run pyinstaller ca_manager.spec --clean
```
