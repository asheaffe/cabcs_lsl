package com.example.hci_lab_build.presentation


import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.runBlocking

class WebSocketService: Service() {
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        val channelId = "websocket_service_channel"
        val channelName = "WebSocket Foreground Service"
        val channel = NotificationChannel(
            channelId, channelName, NotificationManager.IMPORTANCE_LOW
        )
        val notifManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notifManager.createNotificationChannel(channel)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {

        val channelId = "websocket_service_channel"
        val channelName = "WebSocket Foreground Service"


        // Build and show persistent notification
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("WebSocket Active")
            .setContentText("Maintaining live connection")
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setOngoing(true)
            .build()
        // Connect to WebSocket
        runBlocking {
            WebSocketClient.connect()
        }

        startForeground(1, notification)



        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        runBlocking {
            WebSocketClient.disconnect()
        }
    }

}