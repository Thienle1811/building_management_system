import { Platform, Alert } from 'react-native';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';

// Cấu hình hiển thị thông báo khi App đang mở
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  } as Notifications.NotificationBehavior), // <--- CÁCH 3: Ép kiểu để bỏ qua lỗi đỏ
});

export async function registerForPushNotificationsAsync() {
  let token;

  // 1. Cấu hình kênh thông báo cho Android
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  // 2. Kiểm tra thiết bị thật
  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    // Xin quyền nếu chưa có
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      Alert.alert('Thông báo', 'Bạn cần cấp quyền thông báo để nhận tin từ BQL!');
      return;
    }

    // 3. Lấy Project ID (Dùng @ts-ignore để tránh lỗi TypeScript bắt bẻ thư viện Constants)
    // @ts-ignore
    const projectId = Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;

    try {
      // Lấy Token
      const tokenData = await Notifications.getExpoPushTokenAsync(
        projectId ? { projectId } : undefined
      );
      token = tokenData.data;
      console.log("🔥 EXPO PUSH TOKEN:", token);
    } catch (error) {
      console.log("Lỗi lấy Push Token:", error);
    }
  } else {
    console.log('⚠️ Cảnh báo: Phải dùng thiết bị thật để test Push Notification');
  }

  return token;
}