package org.example.submission3.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NodeNotificationRequest {

    String message;

    String senderId;

    long timestamp;

    String signature;
}
