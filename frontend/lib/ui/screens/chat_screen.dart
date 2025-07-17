// lib/ui/screens/chat_screen.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../widgets/chat_box.dart';
import '../../services/api_service.dart';
// 1. IMPORT THE NEW VAPI CALL SCREEN WE WILL CREATE
import './vapi_call_screen.dart'; 

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> messages = [];
  bool isTyping = false;
  bool isCalling = false; // To show a loading indicator for the voice call button

  final Color primaryColor = const Color(0xFF0D47A1);
  final Color accentColor = const Color(0xFF1976D2);

  // (The sendMessage and ticket creation functions remain the same)
  void sendMessage() async {
    final userMessage = _controller.text.trim();
    if (userMessage.isEmpty) return;

    setState(() {
      messages.add({'role': 'user', 'text': userMessage});
      _controller.clear();
      isTyping = true;
    });

    try {
      final aiResponse = await ApiService.sendMessage(userMessage);
      setState(() {
        messages.add({'role': 'assistant', 'text': aiResponse});
        isTyping = false;
      });
    } catch (e) {
      setState(() {
        messages.add({'role': 'assistant', 'text': '❌ Failed to get response. Please check the backend server.'});
        isTyping = false;
      });
    }
  }

  void _showCreateTicketDialog() {
    final emailController = TextEditingController();
    final issueController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text("Create a Support Ticket", style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: emailController,
                decoration: const InputDecoration(labelText: "Your Email"),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: issueController,
                decoration: const InputDecoration(labelText: "Describe your issue"),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              child: const Text("Cancel"),
              onPressed: () => Navigator.of(context).pop(),
            ),
            FilledButton(
              child: const Text("Create"),
              onPressed: () {
                final email = emailController.text.trim();
                final issue = issueController.text.trim();
                if (email.isNotEmpty && issue.isNotEmpty) {
                  Navigator.of(context).pop();
                  _handleCreateTicket(email: email, issueDescription: issue);
                }
              },
            ),
          ],
        );
      },
    );
  }

  void _handleCreateTicket({required String email, required String issueDescription}) async {
    setState(() {
      messages.add({'role': 'user', 'text': 'Creating ticket for issue: "$issueDescription"'});
      isTyping = true;
    });

    try {
      final confirmationMessage = await ApiService.createTicket(
        email: email,
        issueDescription: issueDescription,
      );
      setState(() {
        messages.add({'role': 'assistant', 'text': confirmationMessage});
        isTyping = false;
      });
    } catch (e) {
      setState(() {
        messages.add({'role': 'assistant', 'text': '❌ Failed to create ticket.'});
        isTyping = false;
      });
    }
  }

  // --- 2. UPDATED: FUNCTION TO NAVIGATE TO THE IN-APP VAPI CALL SCREEN ---
  void _startVoiceCall() async {
    setState(() => isCalling = true);

    try {
      // Fetch the secure keys from your backend
      final vapiConfig = await ApiService.getVapiConfig();

      if (vapiConfig.publicKey.isEmpty || vapiConfig.assistantId.isEmpty) {
        throw Exception("Received empty config from server.");
      }

      // Navigate to the new screen, passing the keys to it.
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => VapiCallScreen(
            publicKey: vapiConfig.publicKey,
            assistantId: vapiConfig.assistantId,
          ),
        ),
      );

    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error starting voice call: ${e.toString()}')),
      );
    } finally {
      setState(() => isCalling = false);
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text(
          "Aven AI Chat",
          style: GoogleFonts.poppins(
              fontWeight: FontWeight.w600, color: Colors.white),
        ),
        backgroundColor: primaryColor,
        elevation: 1,
        centerTitle: true,
        actions: [
          // --- UPDATED: VOICE CALL BUTTON WITH LOADING INDICATOR ---
          isCalling
              ? const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16.0),
                  child: Center(child: SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white))),
                )
              : IconButton(
                  icon: const Icon(Icons.phone_in_talk, color: Colors.white),
                  onPressed: _startVoiceCall,
                  tooltip: 'Start a voice call',
                ),
          IconButton(
            icon: const Icon(Icons.support_agent, color: Colors.white),
            onPressed: _showCreateTicketDialog,
            tooltip: 'Create a support ticket',
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        // ... (rest of the body remains the same)
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
                
                return ChatBox(
                  text: message['text']!,
                  isUser: message['role'] == 'user',
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
              child: _buildMessageInput(),
            ),
          )
        ],
      ),
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
