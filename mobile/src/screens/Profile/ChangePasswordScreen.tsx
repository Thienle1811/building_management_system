import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import authApi from '../../api/authApi';

const ChangePasswordScreen = ({ navigation }: any) => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!oldPassword || !newPassword || !confirmPassword) {
      Alert.alert("Lỗi", "Vui lòng nhập đầy đủ thông tin");
      return;
    }
    if (newPassword !== confirmPassword) {
      Alert.alert("Lỗi", "Mật khẩu xác nhận không khớp");
      return;
    }

    setLoading(true);
    try {
      await authApi.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      Alert.alert("Thành công", "Đổi mật khẩu thành công!", [
        { text: "OK", onPress: () => navigation.goBack() }
      ]);
    } catch (error: any) {
      const msg = error.response?.data?.old_password?.[0] || "Đổi mật khẩu thất bại";
      Alert.alert("Lỗi", msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.label}>Mật khẩu hiện tại</Text>
        <TextInput 
          style={styles.input} 
          secureTextEntry 
          value={oldPassword} 
          onChangeText={setOldPassword} 
        />

        <Text style={styles.label}>Mật khẩu mới</Text>
        <TextInput 
          style={styles.input} 
          secureTextEntry 
          value={newPassword} 
          onChangeText={setNewPassword} 
        />

        <Text style={styles.label}>Nhập lại mật khẩu mới</Text>
        <TextInput 
          style={styles.input} 
          secureTextEntry 
          value={confirmPassword} 
          onChangeText={setConfirmPassword} 
        />

        <TouchableOpacity 
          style={styles.button} 
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Xác nhận đổi</Text>}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa', padding: 20 },
  form: { backgroundColor: '#fff', padding: 20, borderRadius: 10 },
  label: { marginBottom: 8, fontWeight: '600', color: '#495057' },
  input: { 
    borderWidth: 1, borderColor: '#ced4da', borderRadius: 8, 
    padding: 12, marginBottom: 20, fontSize: 16 
  },
  button: { 
    backgroundColor: '#0d6efd', padding: 15, borderRadius: 8, 
    alignItems: 'center', marginTop: 10 
  },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 }
});

export default ChangePasswordScreen;