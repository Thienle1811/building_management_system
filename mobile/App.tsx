import React from 'react';
import { NavigationContainer, RouteProp } from '@react-navigation/native';
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
import ProfileScreen from './src/screens/Profile/ProfileScreen';
import ChangePasswordScreen from './src/screens/Profile/ChangePasswordScreen';
import InvoiceListScreen from './src/screens/Billing/InvoiceListScreen';

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

// --- CẤU HÌNH TAB BAR ---
function MainTabNavigator() {
  return (
    <Tab.Navigator
      id="MainTab"
      screenOptions={({ route }: { route: RouteProp<any, any> }) => ({
        headerShown: true,
        tabBarActiveTintColor: '#0d6efd',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: { paddingBottom: 5, height: 60 },
        tabBarLabelStyle: { fontSize: 12, fontWeight: '600' },
        tabBarIcon: ({ focused, color, size }: { focused: boolean; color: string; size: number }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'alert-circle'; 

          if (route.name === 'Home') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'Billing') iconName = focused ? 'receipt' : 'receipt-outline';
          else if (route.name === 'Notifications') iconName = focused ? 'notifications' : 'notifications-outline';
          else if (route.name === 'Feedback') iconName = focused ? 'chatbox-ellipses' : 'chatbox-ellipses-outline';
          else if (route.name === 'Profile') iconName = focused ? 'person' : 'person-outline';

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: 'Trang chủ' }} />
      
      {/* Tab Hóa đơn - Mới thêm */}
      <Tab.Screen name="Billing" component={InvoiceListScreen} options={{ title: 'Hóa đơn' }} />

      <Tab.Screen name="Notifications" component={NotificationScreen} options={{ title: 'Thông báo' }} />
      <Tab.Screen name="Feedback" component={FeedbackListScreen} options={{ title: 'Phản hồi', headerShown: false }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: 'Tài khoản', headerShown: false }} />
    </Tab.Navigator>
  );
}

// --- CẤU HÌNH APP CHÍNH ---
export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator 
        id="RootStack" 
        initialRouteName="Login"
      >
        <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
        <Stack.Screen name="Main" component={MainTabNavigator} options={{ headerShown: false }} />
        
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

        <Stack.Screen 
          name="ChangePassword" 
          component={ChangePasswordScreen} 
          options={{ 
            title: 'Đổi mật khẩu',
            headerStyle: { backgroundColor: '#fff' },
            headerTintColor: '#000',
          }} 
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}