<?php
header('Content-Type: application/json');

$input = json_decode(file_get_contents("php://input"), true);
if (!isset($input['prompt'])) {
  echo json_encode(["error" => "Prompt missing"]);
  exit;
}

$apiKey = "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";

$data = [
  "model" => "gpt-image-1",
  "prompt" => trim($input['prompt']),
  "size" => "1024x1024"
];

$ch = curl_init("https://api.openai.com/v1/images/generations");
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_POST => true,
  CURLOPT_HTTPHEADER => [
    "Content-Type: application/json",
    "Authorization: Bearer $apiKey"
  ],
  CURLOPT_POSTFIELDS => json_encode($data),
  CURLOPT_TIMEOUT => 60
]);

$response = curl_exec($ch);
$http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http !== 200) {
  echo json_encode(["error" => "OpenAI API Error"]);
  exit;
}

echo $response;
