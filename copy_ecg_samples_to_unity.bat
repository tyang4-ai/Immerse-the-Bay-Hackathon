@echo off
REM Helper script to copy ECG sample files to Unity Resources folder
REM Run this from the main branch workspace

echo ============================================
echo ECG Sample Files → Unity Resources Copier
echo HoloHuman XR - Immerse the Bay 2025
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "Backend\dummy_data" (
    echo ERROR: Backend\dummy_data folder not found!
    echo Please run this script from the main branch root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Prompt for Unity project path
echo Please enter the path to your unity-project-upload workspace
echo Example: C:\Users\22317\Documents\Unity\HoloHuman-Unity
echo.
set /p UNITY_PATH="Unity Project Path: "

REM Verify Unity project exists
if not exist "%UNITY_PATH%\Assets" (
    echo ERROR: Assets folder not found at %UNITY_PATH%\Assets
    echo Please check the path and try again.
    pause
    exit /b 1
)

REM Create Resources/ECGSamples folder if it doesn't exist
if not exist "%UNITY_PATH%\Assets\Resources" mkdir "%UNITY_PATH%\Assets\Resources"
if not exist "%UNITY_PATH%\Assets\Resources\ECGSamples" mkdir "%UNITY_PATH%\Assets\Resources\ECGSamples"

echo.
echo Created folder: %UNITY_PATH%\Assets\Resources\ECGSamples
echo.

REM Copy ECG sample files
echo Copying ECG sample files...
echo.

copy "Backend\dummy_data\sample_normal.json" "%UNITY_PATH%\Assets\Resources\ECGSamples\" >nul
if %errorlevel% equ 0 (
    echo [OK] sample_normal.json
) else (
    echo [FAIL] sample_normal.json
)

copy "Backend\dummy_data\sample_rbbb.json" "%UNITY_PATH%\Assets\Resources\ECGSamples\" >nul
if %errorlevel% equ 0 (
    echo [OK] sample_rbbb.json
) else (
    echo [FAIL] sample_rbbb.json
)

copy "Backend\dummy_data\sample_af.json" "%UNITY_PATH%\Assets\Resources\ECGSamples\" >nul
if %errorlevel% equ 0 (
    echo [OK] sample_af.json
) else (
    echo [FAIL] sample_af.json
)

copy "Backend\dummy_data\sample_clinical_expert_rbbb.json" "%UNITY_PATH%\Assets\Resources\ECGSamples\" >nul
if %errorlevel% equ 0 (
    echo [OK] sample_clinical_expert_rbbb.json
) else (
    echo [FAIL] sample_clinical_expert_rbbb.json
)

copy "Backend\dummy_data\sample_ecg_response.json" "%UNITY_PATH%\Assets\Resources\ECGSamples\" >nul
if %errorlevel% equ 0 (
    echo [OK] sample_ecg_response.json
) else (
    echo [FAIL] sample_ecg_response.json
)

echo.
echo ============================================
echo COPY COMPLETE!
echo ============================================
echo.
echo Files copied to: %UNITY_PATH%\Assets\Resources\ECGSamples\
echo.
echo Next steps:
echo 1. Open Unity and verify files appear in Project window
echo 2. Check Assets/Resources/ECGSamples/ folder
echo 3. Unity will auto-generate .meta files for each JSON
echo 4. You can now assign these files to ECGHeartController.ecgDataFile
echo.
echo Example: Drag "ECGSamples/sample_normal" to ECGHeartController Inspector
echo.
pause
