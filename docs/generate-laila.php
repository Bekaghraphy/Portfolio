<?php
header('Content-Type: application/json; charset=utf-8');

ini_set('display_errors', 0); // خليه 1 لو عايز تشوف أخطاء PHP مؤقتًا
error_reporting(E_ALL);

$raw = file_get_contents("php://input");
$input = json_decode($raw, true);

if (!$input || empty($input['prompt'])) {
  echo json_encode(["error" => "Prompt missing"]);
  exit;
}

$prompt = trim($input['prompt']);

// ضيف الـ API KEY بتاعك هنا فقط
$apiKey = "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";

if (strpos($apiKey, "sk-") !== 0) {
  echo json_encode(["error" => "API key not configured on server."]);
  exit;
}

$data = [
  "model" => "gpt-image-1",
  "prompt" => $prompt,
  "size" => "1024x1024"
];

$ch = curl_init("https://api.openai.com/v1/images/generations");
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_POST => true,
  CURLOPT_HTTPHEADER => [
    "Content-Type: application/json",
    "Authorization: Bearer " . $apiKey
  ],
  CURLOPT_POSTFIELDS => json_encode($data, JSON_UNESCAPED_UNICODE),
  CURLOPT_TIMEOUT => 40,        // أقصى مدة انتظار
  CURLOPT_CONNECTTIMEOUT => 10, // أقصى مدة لمحاولة الاتصال
]);

$response = curl_exec($ch);

if ($response === false) {
  $error = curl_error($ch);
  curl_close($ch);
  echo json_encode([
    "error" => "cURL failed",
    "details" => $error
  ], JSON_UNESCAPED_UNICODE);
  exit;
}

$http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http !== 200) {
  echo json_encode([
    "error" => "OpenAI error",
    "status" => $http,
    "response" => $response
  ], JSON_UNESCAPED_UNICODE);
  exit;
}

// لو كل شيء تمام: رجّع رد OpenAI زي ما هو
echo $response;
