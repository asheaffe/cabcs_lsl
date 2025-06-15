package com.example.hci_lab_build.presentation



import android.app.NotificationChannel
import android.app.NotificationManager
import android.util.Log
import io.ktor.client.*
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import io.ktor.http.*
import io.ktor.client.engine.okhttp.OkHttp
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.consumeAsFlow
import java.util.concurrent.TimeUnit

object WebSocketClient {
    private val client = HttpClient(OkHttp) { //CIO or OkHttp
        install(WebSockets)
        engine {
            config{
                connectTimeout(10, TimeUnit.SECONDS)    // Set connection timeout
                readTimeout(22, TimeUnit.SECONDS)       // Set read timeout
            }
        }
    }

    // Channel to send outgoing messages from outside
    private val outgoingMessages = Channel<String>(capacity = Channel.UNLIMITED)
    private val host_ip: String = "10.5.13.122" // change to whatever your ip is
    private var sessionJob: Job? = null
    private lateinit var listener: WebSocketListener


    suspend fun connect() {
        sessionJob = CoroutineScope(Dispatchers.IO).launch {

            Log.d("WebSocketClient","Attempting to connect to WebSocket...")
            try {

                client.webSocket(method = HttpMethod.Get, host = host_ip, port = 8765, path = "",) {
                    Log.d("WebSocketClient", "WebSocket connection success!")
                    // Sender coroutine
                    val sender = launch {
                        for (msg in outgoingMessages) {
                            send(Frame.Text(msg))
                        }
                    }

                    // Receiver coroutine
                    val receiver = launch {
                        incoming.consumeAsFlow().collect { frame ->
                            if (frame is Frame.Text) {
                                val message = frame.readText()
                                Log.d("WebSocketClient", message)
                                // Switch to Main thread before calling activity function
                                if (message == "EXECUTE_VIBRATION"){
                                    withContext(Dispatchers.Main) {
                                        listener.onMessage(message)
                                    }
                                }

                            }
                        }
                    }

                    sender.join() // Wait for sender to finish (e.g. when channel is closed)
                    receiver.cancelAndJoin() // Cancel receiver when done
                }
            } catch (e: Exception) {
                Log.e("WebSocketClient", "Exception: $e")
            }
        }

    }

    // Send a message to the server
    suspend fun send(message: String) {
        outgoingMessages.send(message)
    }

    // Close everything gracefully
    suspend fun disconnect() {
        outgoingMessages.close()
        sessionJob?.cancelAndJoin()
        client.close()
    }

    public fun setListener(listener: WebSocketListener) {
        this.listener = listener
    }



}