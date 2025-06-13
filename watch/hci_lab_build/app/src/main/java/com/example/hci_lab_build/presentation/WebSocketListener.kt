package com.example.hci_lab_build.presentation


interface WebSocketListener {
    fun onConnected()
    suspend fun onMessage(message: String)
    fun onDisconnected()
}