import 'dart:io';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart'; // Import the package
import '../../widgets/chat_box.dart';
import '../../services/api_service.dart';
import 'package:file_picker/file_picker.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> messages = [];
  bool isTyping = false;
  String selectedIntent = 'General';

  final List<String> intents = ['General', 'Refund', 'Pricing', 'Tech Support'];

  // --- Theme Colors ---
  final Color primaryColor = const Color(0xFF0D47A1); // A deep, professional blue
  final Color accentColor = const Color(0xFF1976D2); // A brighter blue for accents
  final Color lightAccentColor = Colors.blue.shade50; // A very light blue for backgrounds

  // All functions (sendMessage, pickAndUploadFile) remain unchanged.
  void sendMessage() async {
    final userMessage = _controller.text.trim();
    if (userMessage.isEmpty) return;

    setState(() {
      messages.add({'role': 'user', 'text': '[$selectedIntent] $userMessage'});
      _controller.clear();
      isTyping = true;
    });

    try {
      final aiResponse =
          await ApiService.sendMessage(userMessage, intent: selectedIntent);
      setState(() {
        messages.add({'role': 'assistant', 'text': aiResponse});
        isTyping = false;
      });
    } catch (e) {
      setState(() {
        messages.add({'role': 'assistant', 'text': '❌ Failed to get response'});
        isTyping = false;
      });
    }
  }

  Future<void> pickAndUploadFile() async {
    final result = await FilePicker.platform.pickFiles(
      allowMultiple: false,
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
    );

    if (result != null && result.files.single.path != null) {
      File file = File(result.files.single.path!);
      setState(() {
        messages.add(
            {'role': 'user', 'text': '📤 Uploading: ${file.path.split('/').last}'});
        isTyping = true;
      });

      try {
        String response =
            await ApiService.uploadFile(file, intent: selectedIntent);
        setState(() {
          messages.add({'role': 'assistant', 'text': response});
          isTyping = false;
        });
      } catch (e) {
        setState(() {
          messages.add({'role': 'assistant', 'text': '❌ File upload failed'});
          isTyping = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text(
          "Aven AI Chat",
          // Applying Poppins font to the AppBar title
          style: GoogleFonts.poppins(
              fontWeight: FontWeight.w600, color: Colors.white),
        ),
        backgroundColor: primaryColor,
        elevation: 1,
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              reverse: true,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              itemCount: messages.length + (isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                if (isTyping && index == 0) {
                  return TypingIndicator(primaryColor: primaryColor);
                }
                final messageIndex = isTyping ? index - 1 : index;
                final message = messages.reversed.toList()[messageIndex];
                // You can also pass the font style to your ChatBox widget
                return ChatBox(
                  text: message['text']!,
                  isUser: message['role'] == 'user',
                  // Example of how you might style the ChatBox text:
                  // textStyle: GoogleFonts.poppins(),
                  // userColor: accentColor,
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.15),
                  spreadRadius: 1,
                  blurRadius: 8,
                  offset: const Offset(0, -3),
                ),
              ],
            ),
            child: SafeArea(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  _buildIntentSelector(),
                  const SizedBox(height: 12),
                  _buildMessageInput(),
                ],
              ),
            ),
          )
        ],
      ),
    );
  }

  Widget _buildIntentSelector() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            const SizedBox(width: 4),
            Icon(Icons.label_outline, size: 20, color: Colors.grey.shade600),
            const SizedBox(width: 8),
            Text(
              "Intent:",
              style: GoogleFonts.poppins(fontSize: 15, color: Colors.black54),
            ),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: lightAccentColor,
                borderRadius: BorderRadius.circular(20),
              ),
              child: DropdownButton<String>(
                value: selectedIntent,
                underline: const SizedBox.shrink(),
                icon: Icon(Icons.expand_more, color: primaryColor),
                isDense: true,
                onChanged: (value) {
                  if (value != null) {
                    setState(() => selectedIntent = value);
                  }
                },
                items: intents
                    .map((intent) => DropdownMenuItem<String>(
                          value: intent,
                          child: Text(
                            intent,
                            style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w500,
                                color: primaryColor),
                          ),
                        ))
                    .toList(),
              ),
            ),
          ],
        ),
        IconButton(
          icon: Icon(Icons.attach_file_outlined, color: Colors.grey.shade700),
          onPressed: pickAndUploadFile,
          tooltip: 'Upload file (PDF, JPG, PNG)',
        ),
      ],
    );
  }

  Widget _buildMessageInput() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _controller,
            onSubmitted: (_) => sendMessage(),
            style: GoogleFonts.poppins(fontSize: 16),
            decoration: InputDecoration(
              hintText: 'Type a message...',
              hintStyle: GoogleFonts.poppins(color: Colors.grey.shade500),
              filled: true,
              fillColor: Colors.grey.shade100,
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(30),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(30),
                borderSide: BorderSide(color: accentColor, width: 2),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        CircleAvatar(
          radius: 24,
          backgroundColor: primaryColor,
          child: IconButton(
            icon: const Icon(Icons.send_rounded, color: Colors.white),
            onPressed: sendMessage,
          ),
        ),
      ],
    );
  }
}

class TypingIndicator extends StatelessWidget {
  final Color primaryColor;
  const TypingIndicator({super.key, required this.primaryColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: primaryColor,
            child: const Icon(Icons.smart_toy_outlined, color: Colors.white, size: 22),
          ),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.grey.shade200,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: Text(
              "Aven is typing...",
              style: GoogleFonts.poppins(fontSize: 16, color: Colors.black54),
            ),
          ),
        ],
      ),
    );
  }
}