'use client';

import React, { useState, FormEvent, ChangeEvent, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/lib/auth/AuthContext';
import LeftBar from '@/components/layout/LeftBar';
import TopBar from '@/components/layout/TopBar';
import { generatePontoOAuthUrl } from '@/lib/utils/ponto';
import { useRouter, useSearchParams } from 'next/navigation';

interface UserSettings {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  companyName: string;
}

export default function SettingsPage() {
  // Initialize router and search params for URL manipulation
  const router = useRouter();
  const searchParams = useSearchParams();
  // Get user data from auth context
  const { user } = useAuth();
  // Ref to prevent duplicate token requests
  const hasFetched = useRef(false);
  // Loading state for initial data fetch
  const [isLoading, setIsLoading] = useState(true);
  // State for user settings form
  const [settings, setSettings] = useState<UserSettings>({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    companyName: '',
  });

  // Function to handle Ponto OAuth callback
  // This is called when user returns from Ponto authorization
  const requestAccessToken = useCallback(async () => {
    const code = searchParams.get('code');
    if (!code) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ponto/access-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error('Failed to get access token');
      }

      const data = await response.json();
      console.log('Access token received:', data);
      // Remove the code from URL
      router.replace('/settings');
    } catch (error) {
      console.error('Error requesting access token:', error);
    }
  }, [searchParams, router]);

  // Effect to handle Ponto OAuth callback
  // Only runs once when component mounts
  useEffect(() => {
    if (!hasFetched.current) {
      requestAccessToken();
      hasFetched.current = true;
    }
  }, [requestAccessToken]);

  // Effect to populate settings form with user data
  // Also manages loading state
  useEffect(() => {
    if (user) {
      setSettings({
        email: user.email || '',
        password: '',
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        companyName: user.company_name || '',
      });
      setIsLoading(false);
    }
  }, [user]);

  // Handler for form field changes
  const handleChange = (field: keyof UserSettings, value: string) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Form submission handler
  // Currently just logs the settings (API integration pending)
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // API integration will be added later
    console.log('Settings to be saved:', settings);
  };

  // Handler for Ponto connection button
  const handlePontoConnect = async () => {
    try {
      const oauthUrl = await generatePontoOAuthUrl();
      window.location.href = oauthUrl;
    } catch (error) {
      console.error('Failed to generate Ponto OAuth URL:', error);
    }
  };

  // Don't render anything if user is not authenticated
  if (!user) {
    return null;
  }

  // Show loading spinner while fetching user data
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <LeftBar />
      <div className="flex w-full flex-col">
        <TopBar onSearch={() => {}} searchResult={[]} />
        <div className="flex-1 p-5 space-y-6">
          {/* Profile Settings Section */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={settings.email}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('email', e.target.value)}
                      disabled
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      value={settings.password}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('password', e.target.value)}
                      disabled
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input
                      id="firstName"
                      value={settings.firstName}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('firstName', e.target.value)}
                      disabled
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input
                      id="lastName"
                      value={settings.lastName}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('lastName', e.target.value)}
                      disabled
                    />
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="companyName">Company Name</Label>
                    <Input
                      id="companyName"
                      value={settings.companyName}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('companyName', e.target.value)}
                      disabled
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button type="submit" disabled>
                    Save Changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Ponto Connect Section */}
          <Card>
            <CardHeader>
              <CardTitle>Bank Integration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Connect your bank account to automatically import transactions and invoices.
                </p>
                <Button onClick={handlePontoConnect} className="w-full md:w-auto">
                  Connect with Ponto
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Support & Legal Section */}
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Help & Support</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Need help? Check out our documentation or contact our support team.
                  </p>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full" disabled>
                      Documentation
                    </Button>
                    <Button variant="outline" className="w-full" disabled>
                      Contact Support
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Legal</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Review our legal documents and policies.
                  </p>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full" disabled>
                      Privacy Policy
                    </Button>
                    <Button variant="outline" className="w-full" disabled>
                      Terms of Service
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 