'use client';

import React, { useRef, useState } from 'react';
import Switch from 'react-switch'; // Import react-switch
import { DEFAULT_URGENCY, Urgency, URGENCY_LEVELS } from '../definitions/invoice';
import { lightenColor } from '@/app/lib/utils';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { ArrowDown } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import { getDueDateMessage } from '../../lib/invoice';
import { useId } from 'react';

interface UrgencySelectorProps {
  urgency?: Urgency;
  onChange: (urgency: Urgency) => void;
}

export function UrgencySelector({ urgency = DEFAULT_URGENCY, onChange }: UrgencySelectorProps) {
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [selected, setSelected] = useState<Urgency>();
  const tooltipId = useId();

  return (
    <div
      className='relative'
      ref={dropdownRef}>
      <div className='flex items-center justify-between w-full py-2 rounded-md '>
        {/* Custom Switch */}
        <div className='w-1/2'>
          <Switch
            checked={urgency.is_manual || false}
            onChange={() => {
              onChange({ ...urgency, is_manual: !urgency.is_manual });
            }}
            offColor='#ddd'
            onColor='#4A90E2'
            uncheckedIcon={
              <div className='flex justify-center items-center h-full w-full text-black text-xs'>
                Auto
              </div>
            }
            checkedIcon={
              <div className='flex justify-end items-center h-full w-full text-white text-xs'>
                Manual
              </div>
            }
            handleDiameter={20}
            height={30}
            width={100}
            className='mx-2'
          />
        </div>

        {/* Urgency Indicator */}
        <div className='flex w-1/2'>
          {urgency.is_manual ? (
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <button
                  className='w-36 bg-gray-200 rounded-md shadow-sm hover:bg-gray-300'
                  style={{ backgroundColor: lightenColor(selected?.color_code, 0.8) }}>
                  {selected?.display_name ? (
                    <div
                      className='flex items-center'
                      data-tooltip-id={tooltipId}
                      data-tooltip-content={getDueDateMessage(urgency.level)}>
                      <div
                        className='min-w-2 min-h-2 rounded-full mx-2'
                        style={{ backgroundColor: selected?.color_code }}
                      />
                      {selected?.display_name}
                      <Tooltip id={tooltipId} />
                    </div>
                  ) : (
                    <div className='flex items-center justify-between  p-1'>
                      <span className='text-sm'>Select Urgency</span>
                      <ArrowDown size={16} />
                    </div>
                  )}
                </button>
              </DropdownMenu.Trigger>

              <DropdownMenu.Content className='w-36 mt-2 bg-white rounded-md shadow-lg p-1'>
                {URGENCY_LEVELS.map((item) => (
                  <DropdownMenu.Item
                    key={item.display_name}
                    onClick={() => {
                      onChange({ ...item, is_manual: true });
                      setSelected(item);
                    }}
                    className='flex items-center rounded-md hover:bg-gray-100 cursor-pointer'>
                    <div
                      className='min-w-2 min-h-2 rounded-full mx-1 mr-2'
                      style={{ backgroundColor: item.color_code }}></div>

                    {item.display_name}
                  </DropdownMenu.Item>
                ))}
              </DropdownMenu.Content>
            </DropdownMenu.Root>
          ) : (
            <div
              data-tooltip-id={tooltipId}
              data-tooltip-content={getDueDateMessage(urgency.level)}
              className='flex items-center w-36 bg-gray-200 rounded-md shadow-sm ps-2'
              style={{ backgroundColor: lightenColor(urgency.color_code, 0.8) }}>
              <Tooltip id={tooltipId} />
              <div
                className='min-w-2 min-h-2 rounded-full'
                style={{ backgroundColor: urgency.color_code }}></div>
              <span className='ml-2'>{urgency.display_name}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
