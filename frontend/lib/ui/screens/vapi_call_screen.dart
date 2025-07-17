import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// These two imports are required to embed web content in a Flutter web app.
// They will show an error if you are not running in a web environment.
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
  late final html.IFrameElement _iFrameElement;

  @override
  void initState() {
    super.initState();

    // Create the IFrameElement that will host our vapi.html page.
    _iFrameElement = html.IFrameElement()
      ..style.border = 'none'
      ..style.width = '100%'
      ..style.height = '100%';

    // Construct the URL to the vapi.html file, passing the keys as query parameters.
    // We use Uri.encodeComponent to ensure the keys are safely added to the URL.
    final url = Uri.parse(
        'vapi.html?publicKey=${Uri.encodeComponent(widget.publicKey)}&assistantId=${Uri.encodeComponent(widget.assistantId)}');
    _iFrameElement.src = url.toString();

    // Register the IFrameElement with a unique ID so Flutter can display it.
    // This is a web-only feature.
    // ignore: undefined_prefixed_name
    ui.platformViewRegistry.registerViewFactory(
      'vapi-iframe-view', // A unique ID for the view factory
      (int viewId) => _iFrameElement,
    );
  }

  @override
  Widget build(BuildContext context) {
    // A polished UI to match your app's theme
    const Color bgColor = Color(0xFF121212);
    const Color appBarColor = Color(0xFF1E1E1E);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        title: Text("Aven AI Voice Call", style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        backgroundColor: appBarColor,
        elevation: 1,
        shadowColor: Colors.black.withOpacity(0.5),
        // The back button is automatically added by the Navigator
      ),
      body: Center(
        // The HtmlElementView widget displays the registered iframe.
        child: HtmlElementView(
          viewType: 'vapi-iframe-view',
          key: UniqueKey(), // Use a unique key to ensure it rebuilds if needed
        ),
      ),
    );
  }
}
