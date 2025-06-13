package com.example.hci_lab_build.sensors

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.util.Log
import com.example.hci_lab_build.presentation.AccelerometerDP
import com.example.hci_lab_build.presentation.WebSocketClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import kotlin.math.pow
import kotlin.math.sqrt

class AccelerometerNew(context: Context) : SensorEventListener {

    private var sensorManager: SensorManager =
        context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private var accelerometer: Sensor? =
        sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)

    lateinit var accelerometerData: String

    private var lastUpdateTime: Long = 0L

    private var magnitude: Float = 0F

    fun register() {
        accelerometer?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    fun unregister() {
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        event?.let {
            val currentTime = System.currentTimeMillis()
            if (currentTime - lastUpdateTime >= 1000) {
                val xVal = it.values[0]
                val yVal = it.values[1]
                val zVal = it.values[2]

                val timestampNano = it.timestamp // nanoseconds since boot
                magnitude = sqrt(xVal.pow(2) + yVal.pow(2) + zVal.pow(2))
                accelerometerData = "X: %.2f\nY: %.2f\nZ: %.2f".format(xVal, yVal, zVal) + " " + timestampNano
                lastUpdateTime = currentTime
                Log.i("app tag", accelerometerData)
                if (magnitude.toInt() != 0) {
                    CoroutineScope(Dispatchers.IO).launch {
                        WebSocketClient.send("movement")
                    }
                }
                val json = Json.encodeToString(AccelerometerDP(
                name = "Accelerometer",
                timestamp = timestampNano,
                x = xVal.toInt(),
                y = yVal.toInt(),
                z = zVal.toInt(),
                unit = "m/s^2"))
                CoroutineScope(Dispatchers.IO).launch {
                    WebSocketClient.send(json)
                }

            }

        }
    }


    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // Do nothing
    }
}
