This project aims to be used in a Delayed Response Task, with the watch sending various types of data from different sensors on the watch with the Samsung Health Sensor API.
### Getting Started
This project uses an Android Watch with WearOS 5, and targets minimum Android 11 (API level 30).

1. First, download the [Samsung Health Sensor API](https://developer.samsung.com/health/sensor/overview.html)

2. Set up Developer Options in Settings and enable debugging over wifi
    - [Debug a Wear OS app](https://developer.android.com/training/wearables/get-started/debugging)
      - Note: The command adb may first have to be found via its absolute root if it is not added to path

3. In the build.gradle.kts(:app):
```kotlin
implementation (files("path/to/file/samsung-health-sensor-api-v1.3.0.aar"))
```
