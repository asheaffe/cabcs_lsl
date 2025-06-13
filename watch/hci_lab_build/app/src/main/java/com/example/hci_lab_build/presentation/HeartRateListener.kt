package com.example.hci_lab_build.presentation

import android.util.Log
import com.samsung.android.service.health.tracking.HealthTracker
import com.samsung.android.service.health.tracking.data.DataPoint
import com.samsung.android.service.health.tracking.data.ValueKey
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json

object HeartRateListener: HealthTracker.TrackerEventListener {

    private const val APP_TAG = "app tag"

    override fun onDataReceived(list: List<DataPoint>) {
        // Process your data
        //val heartRate = list[0]
        //Log.i(APP_TAG, "hr[0] received : ${heartRate.getValue(ValueKey.HeartRateSet.HEART_RATE)} bpm")
        //Log.i(APP_TAG, "hr status[0] received: ${list[0].getValue(ValueKey.HeartRateSet.HEART_RATE_STATUS)}")
        //Log.i(APP_TAG, "ibi[0] received : ${heartRate.getValue(ValueKey.HeartRateSet.IBI_LIST)[0]} bpm")
        for (dataPoint in list) {
            Log.i(APP_TAG, "hr recieved : ${dataPoint.getValue(ValueKey.HeartRateSet.HEART_RATE)} bpm")
            Log.i(APP_TAG, "IBI : ${(dataPoint.getValue(ValueKey.HeartRateSet.IBI_LIST))} ms")
            Log.i(APP_TAG, "TimeStamp : ${(dataPoint.timestamp)}")
        }
        CoroutineScope(Dispatchers.IO).launch {
            sendSocketBatch(list)
        }
    }

    private suspend fun sendSocketBatch(list: List<DataPoint>) {
        for (dataPoint in list) {
            val HRjson = Json.encodeToString(HeartRateDP(
                name = "HR",
                timestamp = dataPoint.timestamp,
                hr = dataPoint.getValue(ValueKey.HeartRateSet.HEART_RATE).toInt(),
                hrStatus = dataPoint.getValue(ValueKey.HeartRateSet.HEART_RATE_STATUS).toInt(),
                iBI = dataPoint.getValue(ValueKey.HeartRateSet.IBI_LIST)[0].toInt(),
                unit = "bpm"
            ))
            WebSocketClient.send(HRjson)
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