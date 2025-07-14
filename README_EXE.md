# MasterApp Executable

This README provides instructions for using the single-file executable version of MasterApp.

## Using the Executable

1. The executable is located in the `dist` folder as `masterapp.exe`.
2. To run the application, simply double-click the `masterapp.exe` file or run it from the command line.
3. When running from the command line, you can specify the bot name as an argument (optional):
   ```
   masterapp.exe masterapp
   ```
   
   If no bot name is provided, it will default to 'masterapp'.

## Important Notes

- The executable contains all necessary dependencies and libraries.
- No additional installation is required.
- The executable includes the following components:
  - MasterApp module
  - Base_bot package
  - Required static files
  - All dependencies

## Recent Fixes

- Fixed the command-line argument handling to use a default bot name ('masterapp') when no argument is provided
- Added comprehensive packaging of the base_bot dependency
- Improved error handling and dependencies resolution

## Troubleshooting

If you encounter any issues running the executable:

1. Make sure you have the correct permissions.
2. Check for any error messages in the console.
3. Ensure that no antivirus software is blocking the execution.
4. If you see import errors related to missing modules, rebuild using the `setup_and_build.bat` script.

## Distribution

You can distribute the `masterapp.exe` file to others who need to run the application without requiring them to install Python or any dependencies.

## Complete Setup and Build

If you need to set up a fresh environment and build the executable:

1. Run `setup_and_build.bat` which will:
   - Create a virtual environment
   - Install all dependencies
   - Install the base_bot package 
   - Build the executable

## Rebuilding After Changes

If you need to rebuild the executable after making changes to the code:

1. Run the `build_exe.bat` script from the root directory.
2. The new executable will be created in the `dist` folder. 