import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Image,
  KeyboardAvoidingView,
  Platform,
  TouchableWithoutFeedback,
  Keyboard
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import authApi from '../../api/authApi';
import notificationApi from '../../api/notificationApi';
import { registerForPushNotificationsAsync } from '../../utils/pushNotifications';

const LoginScreen = ({ navigation }: any) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    // 1. Validate đầu vào
    if (!username || !password) {
      Alert.alert('Thông báo', 'Vui lòng nhập đầy đủ Số điện thoại và Mật khẩu');
      return;
    }

    setLoading(true);
    try {
      // 2. Gọi API đăng nhập
      console.log('Đang đăng nhập...');
      const response: any = await authApi.login(username, password);
      
      // 3. Lưu Token vào bộ nhớ máy
      const { access, refresh } = response.data;
      await AsyncStorage.setItem('userToken', access);
      await AsyncStorage.setItem('refreshToken', refresh);
      console.log("✅ Login thành công! Token đã lưu.");

      // 4. Đăng ký Push Notification (Quan trọng)
      try {
        console.log("⏳ Đang đăng ký Push Notification...");
        const pushToken = await registerForPushNotificationsAsync();
        
        if (pushToken) {
          await notificationApi.registerDevice(pushToken);
          console.log("✅ Đã gửi Push Token lên Server:", pushToken);
        } else {
          console.log("⚠️ Không lấy được Push Token (Có thể do quyền hoặc máy ảo)");
        }
      } catch (pushError) {
        // Lỗi push không được chặn luồng đăng nhập chính
        console.log("❌ Lỗi đăng ký Push:", pushError);
      }
      
      // 5. Chuyển sang màn hình chính
      navigation.reset({
        index: 0,
        routes: [{ name: 'Main' }],
      });

    } catch (error: any) {
      console.log('Login Error:', error);
      Alert.alert(
        'Đăng nhập thất bại', 
        'Sai số điện thoại hoặc mật khẩu. Vui lòng kiểm tra lại kết nối mạng nếu cần.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <View style={styles.inner}>
          
          {/* Logo & Header */}
          <View style={styles.header}>
            <View style={styles.logoCircle}>
              <Text style={styles.logoText}>PMS</Text>
            </View>
            <Text style={styles.title}>Cư Dân Online</Text>
            <Text style={styles.subtitle}>Đăng nhập để quản lý căn hộ của bạn</Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Số điện thoại</Text>
              <TextInput
                style={styles.input}
                placeholder="Ví dụ: 0909123456"
                placeholderTextColor="#aaa"
                value={username}
                onChangeText={setUsername}
                keyboardType="phone-pad"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Mật khẩu</Text>
              <TextInput
                style={styles.input}
                placeholder="Nhập mật khẩu..."
                placeholderTextColor="#aaa"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
            </View>

            <TouchableOpacity 
              style={styles.button} 
              onPress={handleLogin}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>ĐĂNG NHẬP NGAY</Text>
              )}
            </TouchableOpacity>
          </View>

          <Text style={styles.footerText}>@2025 Bản quyền thuộc về Ban Quản Lý</Text>
        </View>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f4f8' },
  inner: { flex: 1, justifyContent: 'center', padding: 24 },
  
  header: { alignItems: 'center', marginBottom: 40 },
  logoCircle: {
    width: 80, height: 80, borderRadius: 40, backgroundColor: '#0d6efd',
    justifyContent: 'center', alignItems: 'center', marginBottom: 15,
    shadowColor: "#0d6efd", shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 5, elevation: 8
  },
  logoText: { color: '#fff', fontSize: 24, fontWeight: 'bold' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#333', marginBottom: 5 },
  subtitle: { fontSize: 14, color: '#6c757d' },

  form: { 
    backgroundColor: '#fff', padding: 25, borderRadius: 20, 
    shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 15, elevation: 5 
  },
  inputGroup: { marginBottom: 20 },
  label: { fontWeight: '600', marginBottom: 8, color: '#495057', fontSize: 14 },
  input: { 
    backgroundColor: '#f8f9fa', padding: 15, borderRadius: 12, 
    borderWidth: 1, borderColor: '#e9ecef', fontSize: 16, color: '#333' 
  },
  
  button: { 
    backgroundColor: '#0d6efd', padding: 16, borderRadius: 12, 
    alignItems: 'center', marginTop: 10,
    shadowColor: "#0d6efd", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 3, elevation: 4
  },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16, letterSpacing: 0.5 },

  footerText: { textAlign: 'center', marginTop: 30, color: '#adb5bd', fontSize: 12 }
});

export default LoginScreen;