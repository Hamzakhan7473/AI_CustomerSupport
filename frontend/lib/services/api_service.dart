import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  static Future<String> sendMessage(String message, {String intent = 'General'}) async {
    final url = Uri.parse('http://localhost:5000/api/ask'); // Update to your actual endpoint

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "query": message,
        "intent": intent,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['response'] ?? '✅ Received (no text)';
    } else {
      throw Exception('Failed to get response from API');
    }
  }

  static Future<String> uploadFile(File file, {String intent = 'General'}) async {
    final url = Uri.parse('http://localhost:5000/api/upload'); // Update if needed

    final request = http.MultipartRequest('POST', url)
      ..fields['intent'] = intent
      ..files.add(await http.MultipartFile.fromPath('file', file.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['response'] ?? '✅ File processed successfully.';
    } else {
      throw Exception('❌ Failed to upload file: ${response.body}');
    }
  }
}
