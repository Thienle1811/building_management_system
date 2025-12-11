import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import authApi from '../../api/authApi';

const ProfileScreen = ({ navigation }: any) => {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchProfile = async () => {
    try {
      const res = await authApi.getProfile();
      setProfile(res.data);
    } catch (error) {
      console.log('Lỗi lấy profile:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleLogout = async () => {
    Alert.alert("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?", [
      { text: "Hủy", style: "cancel" },
      { 
        text: "Đăng xuất", 
        style: 'destructive',
        onPress: async () => {
          await AsyncStorage.clear();
          navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
        }
      }
    ]);
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#0d6efd" /></View>;
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchProfile(); }} />}
    >
      {/* 1. HEADER INFO */}
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>{profile?.full_name?.charAt(0) || 'U'}</Text>
        </View>
        <Text style={styles.name}>{profile?.full_name}</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>Căn hộ {profile?.apartment_code}</Text>
        </View>
      </View>

      {/* 2. THÔNG TIN CÁ NHÂN */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Thông tin liên hệ</Text>
        <View style={styles.row}>
          <Ionicons name="call-outline" size={20} color="#666" />
          <Text style={styles.rowText}>{profile?.phone_number}</Text>
        </View>
        <View style={styles.row}>
          <Ionicons name="card-outline" size={20} color="#666" />
          <Text style={styles.rowText}>{profile?.identity_card}</Text>
        </View>
      </View>

      {/* 3. DANH SÁCH XE */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Phương tiện đã đăng ký ({profile?.vehicles?.length || 0})</Text>
        {profile?.vehicles?.length > 0 ? (
          profile.vehicles.map((v: any) => (
            <View key={v.id} style={styles.vehicleItem}>
              <Ionicons 
                name={v.vehicle_type === 'CAR' ? 'car-sport' : 'bicycle'} 
                size={24} color="#0d6efd" 
              />
              <View style={{ marginLeft: 15 }}>
                <Text style={styles.vehiclePlate}>{v.license_plate}</Text>
                <Text style={styles.vehicleDesc}>{v.manufacturer} - {v.color}</Text>
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>Chưa có phương tiện nào.</Text>
        )}
      </View>

      {/* 4. THÀNH VIÊN KHÁC */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Thành viên cùng căn hộ</Text>
        {profile?.members?.length > 0 ? (
          profile.members.map((m: any) => (
            <View key={m.id} style={styles.memberItem}>
              <View style={styles.smallAvatar}>
                <Text style={{color:'#fff'}}>{m.full_name.charAt(0)}</Text>
              </View>
              <Text style={styles.memberText}>{m.full_name}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>Chỉ có một mình bạn.</Text>
        )}
      </View>

      {/* 5. CÀI ĐẶT */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cài đặt</Text>
        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => navigation.navigate('ChangePassword')}
        >
          <Text style={styles.menuText}>Đổi mật khẩu</Text>
          <Ionicons name="chevron-forward" size={20} color="#ccc" />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Đăng xuất</Text>
        </TouchableOpacity>
      </View>
      
      <View style={{height: 40}} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  
  header: { alignItems: 'center', padding: 30, backgroundColor: '#fff', marginBottom: 10 },
  avatarContainer: { 
    width: 80, height: 80, borderRadius: 40, backgroundColor: '#e9ecef', 
    justifyContent: 'center', alignItems: 'center', marginBottom: 15
  },
  avatarText: { fontSize: 32, fontWeight: 'bold', color: '#0d6efd' },
  name: { fontSize: 22, fontWeight: 'bold', marginBottom: 5 },
  badge: { backgroundColor: '#e7f1ff', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 10 },
  badgeText: { color: '#0d6efd', fontWeight: '600', fontSize: 12 },

  section: { backgroundColor: '#fff', padding: 20, marginBottom: 10 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', marginBottom: 15, color: '#343a40' },
  
  row: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  rowText: { marginLeft: 15, fontSize: 15, color: '#495057' },

  vehicleItem: { 
    flexDirection: 'row', alignItems: 'center', padding: 12, 
    backgroundColor: '#f8f9fa', borderRadius: 10, marginBottom: 10 
  },
  vehiclePlate: { fontWeight: 'bold', fontSize: 16 },
  vehicleDesc: { color: '#6c757d', fontSize: 13 },

  memberItem: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  smallAvatar: { 
    width: 30, height: 30, borderRadius: 15, backgroundColor: '#adb5bd', 
    justifyContent: 'center', alignItems: 'center', marginRight: 10 
  },
  memberText: { fontSize: 15 },

  menuItem: { 
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', 
    paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#f1f3f5' 
  },
  menuText: { fontSize: 15 },
  
  logoutButton: { marginTop: 20, alignItems: 'center', padding: 15 },
  logoutText: { color: 'red', fontWeight: 'bold' },
  emptyText: { color: '#adb5bd', fontStyle: 'italic' }
});

export default ProfileScreen;