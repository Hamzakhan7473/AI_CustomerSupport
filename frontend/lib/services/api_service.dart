// lib/services/api_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
// DO NOT import 'dart:io' for a web application.

class ApiService {
  // For Flutter web, the backend URL is simply localhost with the correct port.
  // We hardcode this because we are running in a browser.
  static const String _baseUrl = 'http://localhost:8000';

  /// Sends a user's conversational query to the /query endpoint.
  static Future<String> sendMessage(String message) async {
    final url = Uri.parse('$_baseUrl/query');
    
    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'query': message,
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return data['answer'] ?? 'Error: "answer" field not found.';
      } else {
        throw Exception('Server returned an error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to the server. Is it running and is CORS configured?');
    }
  }

  /// Creates a support ticket directly via the /create-ticket endpoint.
  static Future<String> createTicket({
    required String email,
    required String issueDescription,
  }) async {
    final url = Uri.parse('$_baseUrl/create-ticket');
    
    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'email': email,
          'issue_description': issueDescription,
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return data['message'] ?? 'Ticket created successfully.';
      } else {
        throw Exception('Server returned an error while creating ticket: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to the server to create ticket.');
    }
  }
}
