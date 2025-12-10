<?php
header('Content-Type: application/json');

$input = json_decode(file_get_contents("php://input"), true);
$prompt = $input["prompt"] ?? "صورة عشوائية";

$apiKey = "key";

$data = [
  "prompt" => $prompt,
  "n" => 1,
  "size" => "512x512"
];

$ch = curl_init("https://api.openai.com/v1/images/generations");
curl_setopt($ch, CURLOPT_HTTPHEADER, [
  "Authorization: Bearer $apiKey",
  "Content-Type: application/json"
]);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);

echo $response;
