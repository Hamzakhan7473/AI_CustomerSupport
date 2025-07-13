import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSend;
  // Add an optional callback for an attachment button
  final VoidCallback? onAttach;

  const ChatInput({
    Key? key,
    required this.onSend,
    this.onAttach,
  }) : super(key: key);

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  bool _isSendButtonEnabled = false;

  @override
  void initState() {
    super.initState();
    // Listen for text changes to enable/disable the send button
    _controller.addListener(() {
      final isTextEmpty = _controller.text.trim().isEmpty;
      if (isTextEmpty == _isSendButtonEnabled) {
        setState(() {
          _isSendButtonEnabled = !isTextEmpty;
        });
      }
    });
  }

  // Dispose the controller to prevent memory leaks
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isNotEmpty) {
      widget.onSend(text);
      _controller.clear();
      // After sending, the text is empty, so disable the button
      setState(() {
        _isSendButtonEnabled = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Material(
      color: theme.colorScheme.surface,
      elevation: 8, // Add a subtle shadow for depth
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Row(
            children: [
              // Show attachment button only if the callback is provided
              if (widget.onAttach != null)
                IconButton(
                  icon: Icon(Icons.add_circle_outline, color: theme.colorScheme.onSurfaceVariant),
                  onPressed: widget.onAttach,
                  tooltip: 'Attach File',
                ),
              Expanded(
                child: TextField(
                  controller: _controller,
                  // Allow the text field to grow for longer messages
                  minLines: 1,
                  maxLines: 5,
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  decoration: InputDecoration(
                    hintText: "Type a message...",
                    hintStyle: TextStyle(color: theme.colorScheme.onSurfaceVariant.withOpacity(0.7)),
                    // Use a modern, "pill" shape with no border
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30),
                      borderSide: BorderSide.none,
                    ),
                    // Change border color on focus for better feedback
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30),
                      borderSide: BorderSide(color: theme.colorScheme.primary, width: 2),
                    ),
                    filled: true,
                    fillColor: theme.colorScheme.surfaceVariant.withOpacity(0.5),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  ),
                  onSubmitted: _isSendButtonEnabled ? (_) => _sendMessage() : null,
                  textInputAction: TextInputAction.send,
                ),
              ),
              const SizedBox(width: 8),
              // Use a modern FilledButton for a more prominent send action
              FilledButton(
                style: FilledButton.styleFrom(
                  shape: const CircleBorder(),
                  padding: const EdgeInsets.all(12),
                  backgroundColor: theme.colorScheme.primary,
                ),
                // Disable button if there is no text
                onPressed: _isSendButtonEnabled ? _sendMessage : null,
                child: const Icon(Icons.send_rounded, size: 24),
              ),
            ],
          ),
        ),
      ),
    );
  }
}