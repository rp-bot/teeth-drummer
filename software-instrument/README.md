# Teeth Drummer MIDI instrument

## Debug Builds

### Option 1

```sh
mkdir -p Build && cd Build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build . --config Debug
```
### Option 2

1. Install the CMake Tools extension in VSCode
2. Navigate to the CMake tab
3. Open up the Project Outline
4. Select your desired Target
5. Right Click (or the "Compile" Icon) and Build / 

## Release Builds

### Option 1

```sh
mkdir -p Build && cd Build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```
### Option 2

1. Install the CMake Tools extension in VSCode
2. Navigate to the CMake tab
3. In the project status dropdown, find the `configure` field.
4. It should show `Debug`, click it and change it to `Release`.
6. Click `refresh` button to update the configuration. 
> But I recommend clicking `Delete Cache and Reconfigure`, Once you are moving towards a release, you don't want to keep any cache from the debug builds anyway.  
7. Open up the Project Outline
8. Select your desired Target
9. Right Click (or the "Compile" Icon) and Build / 

>(optional?) According to my tests, MacOS needs another step in order to make the VST work properly. 
## Code Signing (MacOS)

```sh
codesign --force --deep --sign - ~/Library/Audio/Plug-Ins/VST3/Teeth\ Drummer.vst3
        # ^force replaces the temporary ad-hoc signature that CMake generates, If it exists. 
```

