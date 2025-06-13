/* While this template provides a good starting point for using Wear Compose, you can always
 * take a look at https://github.com/android/wear-os-samples/tree/main/ComposeStarter to find the
 * most up to date changes to the libraries and their usages.
 */

package com.example.hci_lab_build.presentation

import android.os.Bundle
import android.view.WindowManager
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.compose.foundation.background

import androidx.compose.foundation.layout.Box

import androidx.compose.foundation.layout.fillMaxSize

import androidx.compose.runtime.Composable

import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

import androidx.wear.compose.material.Button

import androidx.wear.compose.material.Text

import kotlinx.coroutines.delay

import kotlinx.coroutines.launch
import android.content.Context
import androidx.compose.foundation.layout.size

import androidx.compose.ui.graphics.Color

import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

import androidx.core.app.ActivityCompat
import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import android.util.Log
import android.widget.Toast

import androidx.core.content.ContextCompat
import com.example.hci_lab_build.sensors.AccelerometerNew

import com.samsung.android.service.health.tracking.ConnectionListener
import com.samsung.android.service.health.tracking.HealthTracker
import com.samsung.android.service.health.tracking.HealthTrackerCapability
import com.samsung.android.service.health.tracking.HealthTrackerException
import com.samsung.android.service.health.tracking.HealthTrackingService
import com.samsung.android.service.health.tracking.data.HealthTrackerType



class MainActivity : ComponentActivity() , WebSocketListener {

    private lateinit var accelerometerManager: AccelerometerNew

    lateinit var healthTrackingService: HealthTrackingService
    // Prepare a connection listener to connect with Health Platform
    private val connectionListener = object : ConnectionListener {
        override fun onConnectionSuccess() {
            // Process connection activities here
            Log.d(APP_TAG, "Connection to health platform is a success")
            val availableTrackers: List<HealthTrackerType> = healthTrackingService.trackingCapability.supportHealthTrackerTypes
            Log.d(APP_TAG, "Available Trackers: $availableTrackers")
//            val accelTracker: HealthTracker =
//                healthTrackingService.getHealthTracker(HealthTrackerType.ACCELEROMETER)
//            accelTracker.setEventListener(AccelerometerListener)
            val hrTracker: HealthTracker =
                healthTrackingService.getHealthTracker(HealthTrackerType.HEART_RATE)
            hrTracker.setEventListener(HeartRateListener)
            val skinTempTracker: HealthTracker =
                healthTrackingService.getHealthTracker(HealthTrackerType.SKIN_TEMPERATURE)
            skinTempTracker.setEventListener(SkinTempListener)
        }

        override fun onConnectionEnded() {
            // Process disconnection activities here
            Log.d(APP_TAG, "onConnectionEnded")
            //accelerometerManager.unregister()
        }

        override fun onConnectionFailed(e: HealthTrackerException) {
            if (e.errorCode == HealthTrackerException.OLD_PLATFORM_VERSION ||
                e.errorCode == HealthTrackerException.PACKAGE_NOT_INSTALLED) {
                Toast.makeText(
                    applicationContext,
                    "Health Platform version is outdated or not installed",
                    Toast.LENGTH_LONG
                ).show()
            }
            Log.d(APP_TAG, "onConnectionFailed: $e")
            if (e.hasResolution()) {
                e.resolve(this@MainActivity)
            }
        }
    }

    companion object {
        private const val APP_TAG = "app tag"
    }



    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()

        super.onCreate(savedInstanceState)

        setTheme(android.R.style.Theme_DeviceDefault)

        WebSocketClient.setListener(this)

        val intent = Intent(this, WebSocketService::class.java)
        ContextCompat.startForegroundService(this, intent)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        accelerometerManager = AccelerometerNew(this)


//        disconnectButton.setOnClickListener {
//            webSocketClient.disconnect()
//        }

//        // Check for Activity Recognition permission
        if (ActivityCompat.checkSelfPermission(
                applicationContext,
                Manifest.permission.ACTIVITY_RECOGNITION
            ) == PackageManager.PERMISSION_DENIED
        ) {
            Log.d(APP_TAG, "Permission not granted")
            // Request permission if not granted
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.ACTIVITY_RECOGNITION),
                0
            )
        } else {
            // Permission already granted, proceed
            Toast.makeText(this, "Permission granted!", Toast.LENGTH_SHORT).show()
            //Log.d(APP_TAG, "Permission already granted")
        }

            // Connect to Health Platform
        healthTrackingService = HealthTrackingService(connectionListener, applicationContext)
        healthTrackingService.connectService()


        // Get a list of supported trackers
        // The list returned by the function includes all the available health tracker types from the watch
        try {
            if (healthTrackingService.trackingCapability == null){
                Log.d(APP_TAG, "Null")
            }
//
            val trackingCapability: HealthTrackerCapability  = healthTrackingService.getTrackingCapability()//.getSupportedHealthTrackerTypes()
            Log.d(APP_TAG, "Tracking capability: $trackingCapability")
            //Log.d(APP_TAG, healthTrackingService.connectService().toString())

//            val availableTrackers: List<HealthTrackerType> = trackingCapability.supportHealthTrackerTypes
//            Log.d(APP_TAG, "Available Trackers: $availableTrackers")
            Toast.makeText(applicationContext, "Good", Toast.LENGTH_SHORT).show()


        } catch (e: Exception){
            Toast.makeText(applicationContext, "Bad", Toast.LENGTH_SHORT).show()
            Log.d(APP_TAG, "Exception: $e")
            Log.d(APP_TAG, "Service state: $healthTrackingService")
            Log.d(APP_TAG, "Geeet capabilities: "+healthTrackingService.trackingCapability)

        }

//
//        // Note:
//        // If you would like to get another kind of sensor data
//        // create a new HealthTracker instance and add a separate
//        // listener to it.






        setContent {
//            val viewModel = viewModel<StopWatchViewModel>()
//            val timerState by viewModel.timerState.collectAsStateWithLifecycle()
//            val stopWatchText by viewModel.stopWatchText.collectAsStateWithLifecycle()
//            StopWatch(
//                state = timerState,
//                text = stopWatchText,
//                onToggleRunning = viewModel::toggleIsRunning,
//                onReset = viewModel::resetTimer,
//                modifier = Modifier.fillMaxSize()
//            )
            VibrationButtonScreen()
        }
    }

    override fun onResume() {
        super.onResume()
        accelerometerManager.register() // start listening
    }

    override fun onPause() {
        super.onPause()
        accelerometerManager.unregister() // stop listening
    }

    override fun onConnected() {
        // Handle connection
        Log.i(APP_TAG, "Websocket is connected")
    }

    override suspend fun onMessage(message: String) {
        // Handle received message
        triggerVibration(this)
    }

    override fun onDisconnected() {
        // Handle disconnection
    }

}


@Composable
fun VibrationButtonScreen() {
    val context = LocalContext.current
    // State for background color
    var backgroundColor by remember { mutableStateOf(Color.Cyan) }
    // Remember coroutine scope
    val scope = rememberCoroutineScope()

    // UI layout
    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .fillMaxSize()
            .background(backgroundColor)
    ) {
        Button(
            onClick = {
                triggerVibration(context)
                scope.launch {
                    backgroundColor = Color.Magenta
                    delay(500) // Wait for .5 seconds
                    backgroundColor = Color.Yellow // Revert to original color
                }
            },
            modifier = Modifier.size(200.dp, 80.dp)
        ) {
            Text("Click to Vibrate")
        }
    }
}

//@RequiresApi(api = Build.VERSION_CODES.31)
//@RequiresPermission(Manifest.permission.VIBRATE)
private fun triggerVibration(context: Context) {


    val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator

    if (vibrator.hasVibrator()) { // Check if the device has a vibrator
        val vibrationEffect = VibrationEffect.createOneShot(
            500, // Duration in milliseconds
            VibrationEffect.DEFAULT_AMPLITUDE // Default amplitude
        )
        vibrator.vibrate(vibrationEffect)
    }
}




//@Composable
//private fun StopWatch(
//    state: TimerState,
//    text: String,
//    onToggleRunning: () -> Unit,
//    onReset: () -> Unit,
//    modifier: Modifier = Modifier
//) {
//    Column(
//        modifier = modifier,
//        verticalArrangement = Arrangement.Center,
//        horizontalAlignment = Alignment.CenterHorizontally
//    ) {
//        Text(
//            text = text,
//            fontSize = 20.sp,
//            fontWeight = FontWeight.SemiBold,
//            textAlign = TextAlign.Center
//        )
////
//        Spacer(modifier = Modifier.height(8.dp))
//        Row(
//            modifier = Modifier.fillMaxWidth(),
//            horizontalArrangement = Arrangement.Center
//        ){
//            Button(onClick = onToggleRunning){
//                Icon(
//                    imageVector = if(state == TimerState.RUNNING) {
//                        Icons.Default.Pause
//                    } else {Icons.Default.PlayArrow},
//                    contentDescription = null
//                )
//            }
//            Spacer(modifier = Modifier.height(8.dp))
//            Button(
//                onClick = onReset,
//                enabled = state != TimerState.RESET,
//                colors = ButtonDefaults.buttonColors(
//                    backgroundColor = MaterialTheme.colors.surface
//
//                )
//
//            ){
//                Icon(
//                    imageVector = Icons.Default.Stop,
//                    contentDescription = null
//                )
//            }
//        }
//
//    }
//}


//@Composable
//fun WearApp(greetingName: String) {
//    Broken_Test_3Theme {
//        Box(
//            modifier = Modifier
//                .fillMaxSize()
//                .background(MaterialTheme.colors.background),
//            contentAlignment = Alignment.Center
//        ) {
//            TimeText()
//            Greeting(greetingName = greetingName)
//        }
//    }
//}
//
//@Composable
//fun Greeting(greetingName: String) {
//    Text(
//        modifier = Modifier.fillMaxWidth(),
//        textAlign = TextAlign.Center,
//        color = MaterialTheme.colors.primary,
//        text = stringResource(R.string.hello_world, greetingName)
//    )
//}
//
//@Preview(device = WearDevices.SMALL_ROUND, showSystemUi = true)
//@Composable
//fun DefaultPreview() {
//    WearApp("Preview Android")
//}