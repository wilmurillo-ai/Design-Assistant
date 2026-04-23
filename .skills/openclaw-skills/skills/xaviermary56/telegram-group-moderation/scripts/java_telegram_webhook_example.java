import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class JavaTelegramWebhookExample {
    private static String env(String key, String fallback) {
        String value = System.getenv(key);
        return value == null || value.isEmpty() ? fallback : value;
    }

    private static boolean verifySecret(String provided) {
        String expected = env("TELEGRAM_WEBHOOK_SECRET", "");
        return expected.isEmpty() || expected.equals(provided);
    }

    private static String postJson(String targetUrl, String jsonBody, String bearerToken, int timeoutMs) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(targetUrl).openConnection();
        connection.setRequestMethod("POST");
        connection.setConnectTimeout(timeoutMs);
        connection.setReadTimeout(timeoutMs);
        connection.setDoOutput(true);
        connection.setRequestProperty("Content-Type", "application/json");
        if (bearerToken != null && !bearerToken.isEmpty()) {
            connection.setRequestProperty("Authorization", "Bearer " + bearerToken);
        }

        try (OutputStream os = connection.getOutputStream()) {
            os.write(jsonBody.getBytes(StandardCharsets.UTF_8));
        }

        InputStream inputStream = connection.getResponseCode() >= 200 && connection.getResponseCode() < 300
            ? connection.getInputStream()
            : connection.getErrorStream();

        byte[] body = inputStream.readAllBytes();
        return new String(body, StandardCharsets.UTF_8);
    }

    private static String telegramMethodUrl(String method) {
        String apiBase = env("TELEGRAM_API_BASE", "https://api.telegram.org");
        String botToken = env("TELEGRAM_BOT_TOKEN", "");
        return apiBase.replaceAll("/+$", "") + "/bot" + botToken + "/" + method;
    }

    public static void main(String[] args) throws Exception {
        if (!verifySecret(env("TELEGRAM_WEBHOOK_SECRET", ""))) {
            throw new RuntimeException("invalid webhook secret");
        }

        String moderationEndpoint = env("MODERATION_CORE_ENDPOINT", "");
        String moderationToken = env("MODERATION_CORE_TOKEN", "");
        String moderationPayload = "{" +
            "\"platform\":\"telegram\"," +
            "\"id\":1," +
            "\"title\":\"\"," +
            "\"content\":\"加V了解一下\"," +
            "\"imgs\":[]," +
            "\"videos\":[]," +
            "\"other\":{\"chat_id\":-100123,\"user_id\":777,\"username\":\"spam_user\"}" +
            "}";

        String moderationResponse = postJson(moderationEndpoint, moderationPayload, moderationToken, 15000);
        System.out.println(moderationResponse);

        String deletePayload = "{\"chat_id\":-100123,\"message_id\":1}";
        postJson(telegramMethodUrl("deleteMessage"), deletePayload, "", 10000);

        String warnText = env("TELEGRAM_WARN_MESSAGE_TEMPLATE", "请勿发布广告、引流或联系方式内容。");
        String sendMessagePayload = "{" +
            "\"chat_id\":-100123," +
            "\"text\":\"" + warnText.replace("\"", "\\\"") + "\"," +
            "\"reply_to_message_id\":1" +
            "}";
        postJson(telegramMethodUrl("sendMessage"), sendMessagePayload, "", 10000);
    }
}
