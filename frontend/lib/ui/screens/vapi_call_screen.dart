import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:ui' as ui;
import 'dart:html' as html;

class VapiCallScreen extends StatefulWidget {
  final String publicKey;
  final String assistantId;

  const VapiCallScreen({
    super.key,
    required this.publicKey,
    required this.assistantId,
  });

  @override
  State<VapiCallScreen> createState() => _VapiCallScreenState();
}

class _VapiCallScreenState extends State<VapiCallScreen> {
  late final String _iframeViewType;
  late final html.IFrameElement _iframeElement;

  @override
  void initState() {
    super.initState();

    _iframeViewType = 'vapi-iframe-${DateTime.now().millisecondsSinceEpoch}';

    final iframeUrl = Uri.encodeFull(
      '/vapi.html?publicKey=${widget.publicKey}&assistantId=${widget.assistantId}',
    );

    print('✅ iframe URL: $iframeUrl');

    _iframeElement = html.IFrameElement()
      ..src = iframeUrl
      ..style.border = 'none'
      ..style.width = '100%'
      ..style.height = '100vh'
      ..style.minHeight = '600px'
      ..style.display = 'block'
      ..allow = 'microphone; autoplay'
      ..allowFullscreen = true;

    // ignore: undefined_prefixed_name
    ui.platformViewRegistry.registerViewFactory(
      _iframeViewType,
      (int viewId) => _iframeElement,
    );
  }

  @override
  Widget build(BuildContext context) {
    const bgColor = Color(0xFF121212);
    const appBarColor = Color(0xFF1E1E1E);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: appBarColor,
        title: Text(
          "Aven AI Voice Call",
          style: GoogleFonts.inter(fontWeight: FontWeight.w600),
        ),
        elevation: 1,
      ),
      body: HtmlElementView(
        viewType: _iframeViewType,
        key: UniqueKey(),
      ),
    );
  }
}
