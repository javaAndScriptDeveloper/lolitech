package org.example.submission3.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class NodeNotificationRequest {

    String message;
}
