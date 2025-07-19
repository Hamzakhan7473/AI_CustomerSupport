import 'package:get/get.dart';
import 'package:vapi_flutter_sdk/vapi_flutter_sdk.dart';

enum CallState { connecting, connected, ended }

class VapiController extends GetxController {
  final callState = CallState.connecting.obs;
  late final Vapi vapi;

  @override
  void onInit() {
    super.onInit();
    vapi = Vapi(publicApiKey: "YOUR_PUBLIC_API_KEY_HERE"); // Replace this
    _setupListeners();
  }

  void _setupListeners() {
    vapi.on("call-start", (_) {
      callState.value = CallState.connected;
      print("✅ Call started");
    });

    vapi.on("call-end", (_) {
      callState.value = CallState.ended;
      print("📞 Call ended");
    });

    vapi.on("error", (e) {
      print("❌ Error: $e");
      callState.value = CallState.ended;
      Get.snackbar("Call Error", e.toString());
    });
  }

  void startCall(String assistantId) {
    callState.value = CallState.connecting;
    vapi.startConversation(assistantId: assistantId);
  }

  void endCall() {
    vapi.hangup();
  }

  @override
  void onClose() {
    vapi.removeAllListeners();
    super.onClose();
  }
}
