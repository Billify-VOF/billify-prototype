import { useState } from 'react';
import { LiaFileInvoiceSolid } from 'react-icons/lia';
import { IoSettingsOutline } from 'react-icons/io5';
import { LiaWalletSolid } from 'react-icons/lia';
import { IoShieldCheckmarkOutline } from 'react-icons/io5';
import { HiOutlineSupport, HiOutlineChartPie } from 'react-icons/hi';
import { Unlock } from '@/components/ui/icons';
import Image from 'next/image';
import logo from '../../assets/images/logo.png';

interface LeftBarProps {
  onPontoConnect: () => void;
}

const LeftBar = ({ onPontoConnect }: LeftBarProps) => {
  const [activeItem, setActiveItem] = useState('Dashboard');

  const menuItems = [
    { label: 'Dashboard', icon: HiOutlineChartPie },
    { label: 'Invoices', icon: LiaFileInvoiceSolid },
    { label: 'Wallets', icon: LiaWalletSolid },
    { label: 'Settings', icon: IoSettingsOutline },
    { label: 'Privecy Policy', icon: IoShieldCheckmarkOutline },
    { label: 'Help & Support', icon: HiOutlineSupport },
  ];

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
              onClick={() => setActiveItem(item.label)}
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
        <div
          onClick={() => onPontoConnect()}
          className={`flex cursor-pointer flex-row justify-center gap-x-3 rounded-xl px-2 py-4 transition-all hover:bg-blue-50 lg:justify-start`}
        >
          <Unlock size={24} className={'text-gray-600'} />
          <span className={`lg:block' text-gray-70`}>Ponto Connect</span>
        </div>
      </div>
    </div>
  );
};

export default LeftBar;
