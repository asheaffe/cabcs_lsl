package com.example.hci_lab_build.presentation

import android.util.Log
import com.samsung.android.service.health.tracking.HealthTracker
import com.samsung.android.service.health.tracking.data.DataPoint
import com.samsung.android.service.health.tracking.data.ValueKey
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json

object SkinTempListener: HealthTracker.TrackerEventListener {

    private const val APP_TAG = "app tag"

    override fun onDataReceived(list: List<DataPoint>) {
        // Process your data
        Log.i(APP_TAG, "skin temp ambient[0] received : ${list[0].getValue(ValueKey.SkinTemperatureSet.AMBIENT_TEMPERATURE)}")
        Log.i(APP_TAG, "skin temp obj[0] received: ${list[0].getValue(ValueKey.SkinTemperatureSet.OBJECT_TEMPERATURE)}")

        CoroutineScope(Dispatchers.IO).launch {
            sendSocketBatch(list)
        }
    }

    private suspend fun sendSocketBatch(list: List<DataPoint>) {
        for (dataPoint in list) {
            val json = Json.encodeToString(SkinTempDP(
                name = "Skin Temp",
                timestamp = dataPoint.timestamp,
                ambientTemp = dataPoint.getValue(ValueKey.SkinTemperatureSet.AMBIENT_TEMPERATURE).toInt(),
                objTemp = dataPoint.getValue(ValueKey.SkinTemperatureSet.OBJECT_TEMPERATURE).toInt(),
                unit = "Celsius"
            ))
            WebSocketClient.send(json)
        }

    }

    override fun onFlushCompleted() {
        // Process flush completion
    }

    override fun onError(trackerError: HealthTracker.TrackerError) {
        Log.i(APP_TAG, "onError called")
        when (trackerError) {
            HealthTracker.TrackerError.PERMISSION_ERROR -> {
                Log.e(APP_TAG, "Permissions Check Failed")
            }
            HealthTracker.TrackerError.SDK_POLICY_ERROR -> {
                Log.e(APP_TAG, "SDK Policy denied")
            }
            else -> {
                // Handle other errors if necessary
            }
        }
    }

}