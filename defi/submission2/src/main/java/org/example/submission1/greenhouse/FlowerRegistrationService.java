package org.example.submission1.greenhouse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.submission1.RegisterFlowerMessage;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class FlowerRegistrationService {

    private final FlowerRepository flowerRepository;

    @RabbitListener(queues = RabbitConfiguration.QUEUE_NAME)
    public void register(RegisterFlowerMessage message) {
        log.info("Received flower via rabbit: name={}, soilType={}, origin={}, multiplying={}",
                message.getName(), message.getSoilType(), message.getOrigin(), message.getMultiplying());

        FlowerEntity entity = toEntity(message);
        FlowerEntity saved = flowerRepository.save(entity);

        log.info("Saved flower to DB: id={}, name={}", saved.getId(), saved.getName());
    }

    private FlowerEntity toEntity(RegisterFlowerMessage msg) {
        return FlowerEntity.builder()
                .name(msg.getName())
                .soilType(msg.getSoilType().name())
                .origin(msg.getOrigin())
                .leafColor(msg.getVisualParameters().getLeafColor().name())
                .averageLength(msg.getVisualParameters().getAverageLength())
                .averageTemperature(msg.getGrowingTips().getAverageTemperature())
                .lightFriendly(msg.getGrowingTips().getIsLightFriendly())
                .multiplying(msg.getMultiplying().name())
                .build();
    }
}
