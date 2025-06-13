//package com.example.hci_lab_build.presentation
//
//import android.util.Log
//import com.samsung.android.service.health.tracking.HealthTracker
//import com.samsung.android.service.health.tracking.data.DataPoint
//import com.samsung.android.service.health.tracking.data.ValueKey
//import kotlinx.coroutines.CoroutineScope
//import kotlinx.coroutines.Dispatchers
//import kotlinx.coroutines.launch
//import kotlinx.serialization.json.Json
//
//object AccelerometerListener: HealthTracker.TrackerEventListener {
//
//    private const val APP_TAG = "app tag"
//
//    override fun onDataReceived(list: List<DataPoint>) {
//            // Process your data
//            Log.i(APP_TAG, "X received: ${list.get(0).getValue(ValueKey.AccelerometerSet.ACCELEROMETER_X)*(9.81 / (16383.75 / 4.0))} m/s^2")
////        //Log.i(APP_TAG, "Y received: ${list[0].getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Y)*(9.81 / (16383.75 / 4.0))}")
////        //Log.i(APP_TAG, "Z received: ${list.get(0).getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Z)*(9.81 / (16383.75 / 4.0))}")
//
////        for (dataPoint in list) {
////            Log.i(APP_TAG, "X received: ${dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_X)}")
////            Log.i(APP_TAG, "Y received: ${dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Y)}")
////            Log.i(APP_TAG, "Z received: ${dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Z)}")
////        }
//        CoroutineScope(Dispatchers.IO).launch {
//            sendSocketBatch(list)
//
//        }
//    }
//
//    private suspend fun sendSocketBatch(list: List<DataPoint>) {
//        for (dataPoint in list) {
//            val json = Json.encodeToString(AccelerometerDP(
//                name = "Accelerometer",
//                timestamp = dataPoint.timestamp,
//                x = dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_X).toInt(),
//                y = dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Y).toInt(),
//                z = dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Z).toInt(),
//                unit = "raw"
//            ))
//            WebSocketClient.send(json)
//        }
//
//    }
//
//    override fun onFlushCompleted() {
//        // Process flush completion
//    }
//
//    override fun onError(trackerError: HealthTracker.TrackerError) {
//        Log.i(APP_TAG, "onError called")
//        when (trackerError) {
//            HealthTracker.TrackerError.PERMISSION_ERROR -> {
//                Log.e(APP_TAG, "Permissions Check Failed")
//            }
//            HealthTracker.TrackerError.SDK_POLICY_ERROR -> {
//                Log.e(APP_TAG, "SDK Policy denied")
//            }
//            else -> {
//                // Handle other errors if necessary
//            }
//        }
//    }
//
//}

