import { useState } from 'react';
import { LiaFileInvoiceSolid } from 'react-icons/lia';
import { IoSettingsOutline } from 'react-icons/io5';
import { LiaWalletSolid } from 'react-icons/lia';
import { HiOutlineChartPie } from 'react-icons/hi';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import logo from '../../assets/images/logo.svg';

const LeftBar = () => {
  const router = useRouter();
  const [activeItem, setActiveItem] = useState('Dashboard');

  const menuItems = [
    { label: 'Dashboard', icon: HiOutlineChartPie, path: '/dashboard' },
    { label: 'Invoices', icon: LiaFileInvoiceSolid, path: '/invoices' },
    { label: 'Wallets', icon: LiaWalletSolid, path: '/wallets' },
    { label: 'Settings', icon: IoSettingsOutline, path: '/settings' },
  ];

  const handleItemClick = (label: string, path: string) => {
    setActiveItem(label);
    router.push(path);
  };

  return (
    <div className="flex w-24 flex-col border-r-2 border-gray-200 bg-white px-2 py-6 lg:w-80 lg:px-6">
      <div className="flex justify-center text-xl font-semibold text-gray-700 lg:justify-start">
        <Image src={logo} alt="Billify Logo" width={120} height={40} priority />
      </div>
      <div className="mt-10 flex flex-col justify-center gap-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.label;
          return (
            <div
              key={item.label}
              onClick={() => handleItemClick(item.label, item.path)}
              className={`flex cursor-pointer flex-row justify-center gap-x-3 rounded-xl px-2 py-4 transition-all hover:bg-blue-50 lg:justify-start ${
                isActive ? 'bg-blue-500/5' : ''
              }`}
            >
              <Icon size={24} className={`${isActive ? 'text-blue-600' : 'text-gray-600'}`} />
              <span
                className={`${isActive ? 'hidden font-bold text-gray-800 lg:block' : 'hidden text-gray-700 lg:block'}`}
              >
                {item.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LeftBar;
