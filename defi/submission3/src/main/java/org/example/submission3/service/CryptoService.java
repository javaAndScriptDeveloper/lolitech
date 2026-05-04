package org.example.submission3.service;

import jakarta.annotation.PostConstruct;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

@Slf4j
@Service
public class CryptoService {

    private static final String ALGORITHM      = "RSA";
    private static final String SIGNATURE_ALGO = "SHA256withRSA";
    private static final int    KEY_SIZE        = 2048;

    private KeyPair keyPair;

    @Getter
    private String publicKeyBase64;

    @PostConstruct
    @SneakyThrows
    public void init() {
        var generator = KeyPairGenerator.getInstance(ALGORITHM);
        generator.initialize(KEY_SIZE, new SecureRandom());
        keyPair = generator.generateKeyPair();
        publicKeyBase64 = Base64.getEncoder().encodeToString(keyPair.getPublic().getEncoded());
        log.info("CryptoService: RSA-2048 key pair generated. Public key: {}", publicKeyBase64);
    }

    @SneakyThrows
    public String sign(String payload) {
        var signer = Signature.getInstance(SIGNATURE_ALGO);
        signer.initSign(keyPair.getPrivate());
        signer.update(payload.getBytes(StandardCharsets.UTF_8));
        var result = Base64.getEncoder().encodeToString(signer.sign());
        log.debug("CryptoService: Signed payload [{}]", payload);
        return result;
    }

    @SneakyThrows
    public boolean verify(String payload, String signatureBase64, String senderPublicKeyBase64) {
        var keyBytes  = Base64.getDecoder().decode(senderPublicKeyBase64);
        var publicKey = KeyFactory.getInstance(ALGORITHM).generatePublic(new X509EncodedKeySpec(keyBytes));
        var verifier  = Signature.getInstance(SIGNATURE_ALGO);
        verifier.initVerify(publicKey);
        verifier.update(payload.getBytes(StandardCharsets.UTF_8));
        return verifier.verify(Base64.getDecoder().decode(signatureBase64));
    }
}
