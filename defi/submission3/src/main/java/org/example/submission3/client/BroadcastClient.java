package org.example.submission3.client;

import org.springframework.stereotype.Component;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

@Component
public class BroadcastClient {

    public void sendBroadcastRequest(String requestBody, String broadcastAddress, int broadcastPort) {
        try (DatagramSocket socket = new DatagramSocket()) {
            socket.setBroadcast(true);

            var buffer = requestBody.getBytes();
            var address = InetAddress.getByName(broadcastAddress);

            var packet = new DatagramPacket(buffer, buffer.length, address, broadcastPort);
            socket.send(packet);
        } catch (Exception e) {
           e.printStackTrace();
        }
    }
}
