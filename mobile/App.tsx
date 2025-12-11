import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons'; 

// Import các màn hình
import LoginScreen from './src/screens/Auth/LoginScreen';
import FeedbackListScreen from './src/screens/Feedback/FeedbackListScreen';
import CreateFeedbackScreen from './src/screens/Feedback/CreateFeedbackScreen';
import NotificationScreen from './src/screens/Notification/NotificationScreen';

// Tạo màn hình Home tạm thời
const HomeScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' }}>
    <Ionicons name="home" size={80} color="#0d6efd" style={{ marginBottom: 20 }} />
    <Text style={{ fontSize: 22, fontWeight: 'bold', color: '#0d6efd', marginBottom: 10 }}>
      Chào mừng Cư dân!
    </Text>
    <Text style={{ color: '#6c757d', textAlign: 'center', paddingHorizontal: 40 }}>
      Đây là ứng dụng quản lý căn hộ chính thức.
      {"\n"}Vui lòng chọn các tab bên dưới để sử dụng dịch vụ.
    </Text>
  </View>
);

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// --- CẤU HÌNH TAB BAR (Thanh menu dưới đáy) ---
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: true,
        tabBarActiveTintColor: '#0d6efd',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: { paddingBottom: 5, height: 60 },
        tabBarLabelStyle: { fontSize: 12, fontWeight: '600' },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          // Cấu hình Icon cho từng Tab
          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Feedback') {
            iconName = focused ? 'chatbox-ellipses' : 'chatbox-ellipses-outline';
          } else if (route.name === 'Notifications') {
            iconName = focused ? 'notifications' : 'notifications-outline';
          } else {
            iconName = 'alert-circle';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ title: 'Trang chủ' }} 
      />
      
      {/* Tab Thông báo */}
      <Tab.Screen 
        name="Notifications" 
        component={NotificationScreen} 
        options={{ title: 'Thông báo' }} 
      />
      
      {/* Tab Phản hồi (Ẩn header tab để dùng header riêng của màn hình) */}
      <Tab.Screen 
        name="Feedback" 
        component={FeedbackListScreen} 
        options={{ title: 'Phản hồi', headerShown: false }} 
      />
    </Tab.Navigator>
  );
}

// --- CẤU HÌNH APP CHÍNH (Luồng đi của ứng dụng) ---
export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator initialRouteName="Login">
        
        {/* 1. Màn hình Đăng nhập (Mặc định) */}
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ headerShown: false }} 
        />
        
        {/* 2. Màn hình Chính (Chứa 3 Tab: Home, Notifications, Feedback) */}
        <Stack.Screen 
          name="Main" 
          component={MainTabNavigator} 
          options={{ headerShown: false }} 
        />

        {/* 3. Màn hình Tạo phản hồi (Nằm đè lên trên Tab Bar) */}
        <Stack.Screen 
          name="CreateFeedback" 
          component={CreateFeedbackScreen} 
          options={{ 
            title: 'Gửi phản hồi mới',
            headerStyle: { backgroundColor: '#0d6efd' },
            headerTintColor: '#fff',
            headerTitleStyle: { fontWeight: 'bold' },
          }} 
        />

      </Stack.Navigator>
    </NavigationContainer>
  );
}