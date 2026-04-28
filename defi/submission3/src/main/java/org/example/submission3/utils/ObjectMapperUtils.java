package org.example.submission3.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.SneakyThrows;
import lombok.experimental.UtilityClass;

@UtilityClass
public class ObjectMapperUtils {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    @SneakyThrows
    public static <T> String serialize (T clazz) {
        return OBJECT_MAPPER.writeValueAsString(clazz);
    }

    @SneakyThrows
    public static <T> T deserialize (String rawString, Class<T> clazz) {
        return OBJECT_MAPPER.readValue(rawString, clazz);
    }
}
