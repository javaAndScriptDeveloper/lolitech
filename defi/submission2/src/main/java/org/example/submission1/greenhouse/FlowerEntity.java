package org.example.submission1.greenhouse;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "flowers")
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FlowerEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String soilType;
    private String origin;
    private String leafColor;
    private Long averageLength;
    private Long averageTemperature;
    private Boolean lightFriendly;
    private String multiplying;
}
