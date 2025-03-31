'use client';

import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { ArrowDown } from 'lucide-react';
import React, { useRef, useState , useId } from 'react';
import Switch from 'react-switch'; // Import react-switch
import { Tooltip } from 'react-tooltip';

import { lightenColor } from '@/app/lib/utils';

import { getDueDateMessage } from '../../lib/invoice';
import { DEFAULT_URGENCY, URGENCY_LEVELS } from '../definitions/invoice';
import type { Urgency} from '../definitions/invoice';



interface UrgencySelectorProps {
  urgency?: Urgency;
  onChange: (urgency: Urgency) => void;
}

export function UrgencySelector({ urgency = DEFAULT_URGENCY, onChange }: UrgencySelectorProps) {
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [selected, setSelected] = useState<Urgency>(urgency);
  const tooltipId = useId();

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="flex w-full items-center justify-between rounded-md py-2">
        {/* Custom Switch */}
        <div className="w-1/2">
          <Switch
            checked={urgency.is_manual || false}
            onChange={() => {
              onChange({ ...urgency, is_manual: !urgency.is_manual });
            }}
            offColor="#ddd"
            onColor="#4A90E2"
            uncheckedIcon={
              <div className="flex h-full w-full items-center justify-center text-xs text-black">
                Auto
              </div>
            }
            checkedIcon={
              <div className="flex h-full w-full items-center justify-end text-xs text-white">
                Manual
              </div>
            }
            handleDiameter={20}
            height={30}
            width={100}
            className="mx-2"
          />
        </div>

        {/* Urgency Indicator */}
        <div className="flex w-1/2">
          {urgency.is_manual ? (
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <button
                  className="w-36 rounded-md bg-gray-200 shadow-sm hover:bg-gray-300"
                  style={{ backgroundColor: lightenColor(selected?.color_code, 0.8) }}
                >
                  {selected?.display_name ? (
                    <div
                      className="flex items-center"
                      data-tooltip-id={tooltipId}
                      data-tooltip-content={getDueDateMessage(urgency.level)}
                    >
                      <div
                        className="mx-2 min-h-2 min-w-2 rounded-full"
                        style={{ backgroundColor: selected?.color_code }}
                      />
                      {selected?.display_name}
                      <Tooltip id={tooltipId} />
                    </div>
                  ) : (
                    <div className="flex items-center justify-between p-1">
                      <span className="text-sm">Select Urgency</span>
                      <ArrowDown size={16} />
                    </div>
                  )}
                </button>
              </DropdownMenu.Trigger>

              <DropdownMenu.Content className="mt-2 w-36 rounded-md bg-white p-1 shadow-lg">
                {URGENCY_LEVELS.map((item) => (
                  <DropdownMenu.Item
                    key={item.display_name}
                    onClick={() => {
                      onChange({ ...item, is_manual: true });
                      setSelected(item);
                    }}
                    className="flex cursor-pointer items-center rounded-md hover:bg-gray-100"
                  >
                    <div
                      className="mx-1 mr-2 min-h-2 min-w-2 rounded-full"
                      style={{ backgroundColor: item.color_code }}
                    ></div>

                    {item.display_name}
                  </DropdownMenu.Item>
                ))}
              </DropdownMenu.Content>
            </DropdownMenu.Root>
          ) : (
            <div
              data-tooltip-id={tooltipId}
              data-tooltip-content={getDueDateMessage(urgency.level)}
              className="flex w-36 items-center rounded-md bg-gray-200 ps-2 shadow-sm"
              style={{ backgroundColor: lightenColor(urgency.color_code, 0.8) }}
            >
              <Tooltip id={tooltipId} />
              <div
                className="min-h-2 min-w-2 rounded-full"
                style={{ backgroundColor: urgency.color_code }}
              ></div>
              <span className="ml-2">{urgency.display_name}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
