package org.example.submission3.model;

import lombok.Builder;
import lombok.Data;

import java.net.InetSocketAddress;

@Data
@Builder
public class Node {

    String id;

    InetSocketAddress address;

    String publicKey;
}
