import 'package:flutter/material.dart';

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({
    super.key,
    this.showAvatar = true,
  });

  // Controls whether the bot's avatar is displayed.
  final bool showAvatar;

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    // Create an animation controller that loops continuously.
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (widget.showAvatar)
            CircleAvatar(
              backgroundColor: theme.colorScheme.primaryContainer,
              child: Icon(
                Icons.smart_toy_outlined,
                color: theme.colorScheme.onPrimaryContainer,
                size: 22,
              ),
            ),
          const SizedBox(width: 12),
          // A container styled to look like a chat bubble.
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceVariant,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (index) {
                // Apply a staggered delay to each dot's animation.
                final interval = Interval(
                  0.1 * index,        // Start delay
                  0.5 + (0.1 * index),  // End time
                  curve: Curves.easeOut,
                );

                return _BouncingDot(
                  controller: _controller,
                  interval: interval,
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}

/// A single animated dot that bounces up and down.
class _BouncingDot extends StatelessWidget {
  const _BouncingDot({
    required this.controller,
    required this.interval,
  });

  final AnimationController controller;
  final Interval interval;

  @override
  Widget build(BuildContext context) {
    // A vertical bounce animation.
    final bounce = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: -7.0), weight: 50),
      TweenSequenceItem(tween: Tween(begin: -7.0, end: 0.0), weight: 50),
    ]).animate(CurvedAnimation(parent: controller, curve: interval));

    return AnimatedBuilder(
      animation: bounce,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, bounce.value),
          child: child,
        );
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 3),
        child: CircleAvatar(
          radius: 4,
          backgroundColor:
              Theme.of(context).colorScheme.onSurfaceVariant.withOpacity(0.8),
        ),
      ),
    );
  }
}