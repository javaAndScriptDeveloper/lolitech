package org.example.submission1.greenprovider;

import io.grpc.stub.StreamObserver;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.server.service.GrpcService;
import org.example.submission1.Empty;
import org.example.submission1.FlowerRegistrationServiceGrpc;
import org.example.submission1.RegisterFlowerMessage;
import org.springframework.scheduling.annotation.Scheduled;

import java.util.List;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.concurrent.ThreadLocalRandom;

@Slf4j
@GrpcService
public class FlowerRegistrationServiceImpl extends FlowerRegistrationServiceGrpc.FlowerRegistrationServiceImplBase {

    private final CopyOnWriteArraySet<StreamObserver<RegisterFlowerMessage>> clients = new CopyOnWriteArraySet<>();

    @Override
    public void subscribeMessages(Empty request, StreamObserver<RegisterFlowerMessage> responseObserver) {
        clients.add(responseObserver);
        log.info("New gRPC subscriber connected, total clients: {}", clients.size());

        if (responseObserver instanceof io.grpc.stub.ServerCallStreamObserver<RegisterFlowerMessage> serverObserver) {
            serverObserver.setOnCancelHandler(() -> {
                clients.remove(responseObserver);
                log.info("gRPC subscriber disconnected, total clients: {}", clients.size());
            });
        }
    }

    private static final List<String> NAMES = List.of(
            "sunflower", "rose", "tulip", "daisy", "orchid", "lavender", "lily", "iris"
    );
    private static final List<String> ORIGINS = List.of(
            "Netherlands", "Colombia", "Ecuador", "Kenya", "Ethiopia", "China", "Japan"
    );

    private RegisterFlowerMessage randomMessage() {
        ThreadLocalRandom rng = ThreadLocalRandom.current();

        RegisterFlowerMessage.FlowerSoilType[] soilTypes = {
                RegisterFlowerMessage.FlowerSoilType.FLOWER_SOIL_TYPE_GROUND,
                RegisterFlowerMessage.FlowerSoilType.FLOWER_SOIL_TYPE_PODZOLIC,
                RegisterFlowerMessage.FlowerSoilType.FLOWER_SOIL_TYPE_SOD_PODZOLIC
        };
        RegisterFlowerMessage.VisualParameters.Color[] colors = {
                RegisterFlowerMessage.VisualParameters.Color.COLOR_RED,
                RegisterFlowerMessage.VisualParameters.Color.COLOR_GREEN,
                RegisterFlowerMessage.VisualParameters.Color.COLOR_BLUE
        };
        RegisterFlowerMessage.Multiplying[] multiplyings = {
                RegisterFlowerMessage.Multiplying.MULTIPLYING_BY_LEAFS,
                RegisterFlowerMessage.Multiplying.MULTIPLYING_BY_LIVING,
                RegisterFlowerMessage.Multiplying.MULTIPLYING_BY_SEEDS
        };

        return RegisterFlowerMessage.newBuilder()
                .setName(NAMES.get(rng.nextInt(NAMES.size())))
                .setSoilType(soilTypes[rng.nextInt(soilTypes.length)])
                .setOrigin(ORIGINS.get(rng.nextInt(ORIGINS.size())))
                .setVisualParameters(RegisterFlowerMessage.VisualParameters.newBuilder()
                        .setLeafColor(colors[rng.nextInt(colors.length)])
                        .setAverageLength(rng.nextLong(5, 100))
                        .build())
                .setGrowingTips(RegisterFlowerMessage.GrowingTips.newBuilder()
                        .setAverageTemperature(rng.nextLong(10, 35))
                        .setIsLightFriendly(rng.nextBoolean())
                        .build())
                .setMultiplying(multiplyings[rng.nextInt(multiplyings.length)])
                .build();
    }

    @Scheduled(fixedRate = 5000)
    public void sendUpdates() {
        RegisterFlowerMessage message = randomMessage();

        log.debug("Broadcasting flower update to {} client(s): name={}", clients.size(), message.getName());
        for (StreamObserver<RegisterFlowerMessage> client : clients) {
            try {
                client.onNext(message);
            } catch (Exception e) {
                log.warn("Failed to send to a client, removing: {}", e.getMessage());
                clients.remove(client);
            }
        }
    }
}
