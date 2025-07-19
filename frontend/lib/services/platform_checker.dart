// This file is a stub used for conditional imports.
// It provides a default implementation for non-mobile platforms (like web)
// where 'dart:io' is not available.

class Platform {
  // We can default these to false for web, as we only need to specifically
  // check for Android in our ApiService.
  static bool get isAndroid => false;
  static bool get isIOS => false;
  // Add other platforms as needed, defaulting to false.
}
