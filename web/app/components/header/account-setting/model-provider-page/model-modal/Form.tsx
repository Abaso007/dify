import { useState } from 'react'
import type { FC } from 'react'
import { ValidatingTip } from '../../key-validator/ValidateStatus'
import type {
  CredentialFormSchema,
  CredentialFormSchemaRadio,
  CredentialFormSchemaSecretInput,
  CredentialFormSchemaSelect,
  CredentialFormSchemaTextInput,
  FormValue,
} from '../declarations'
import { FormTypeEnum } from '../declarations'
import { useLanguage } from '../hooks'
import Input from './Input'
import { SimpleSelect } from '@/app/components/base/select'

type FormProps = {
  value: FormValue
  onChange: (val: FormValue) => void
  formSchemas: CredentialFormSchema[]
  validating: boolean
  validatedSuccess?: boolean
  showOnVariableMap: Record<string, string[]>
  isEditMode: boolean
}

const Form: FC<FormProps> = ({
  value,
  onChange,
  formSchemas,
  validating,
  validatedSuccess,
  showOnVariableMap,
  isEditMode,
}) => {
  const language = useLanguage()
  const [changeKey, setChangeKey] = useState('')

  const handleFormChange = (key: string, val: string) => {
    if (isEditMode && (key === '__model_type' || key === '__model_name'))
      return

    setChangeKey(key)
    const shouldClearVariable: Record<string, string | undefined> = {}
    if (showOnVariableMap[key]?.length) {
      showOnVariableMap[key].forEach((clearVariable) => {
        shouldClearVariable[clearVariable] = undefined
      })
    }
    onChange({ ...value, [key]: val, ...shouldClearVariable })
  }

  const renderField = (formSchema: CredentialFormSchema) => {
    if (formSchema.type === FormTypeEnum.textInput || formSchema.type === FormTypeEnum.secretInput) {
      const {
        variable,
        label,
        placeholder,
        required,
        show_on,
      } = formSchema as (CredentialFormSchemaTextInput | CredentialFormSchemaSecretInput)

      if (show_on.length && !show_on.every(showOnItem => value[showOnItem.variable] === showOnItem.value))
        return null

      const disabed = isEditMode && (variable === '__model_type' || variable === '__model_name')

      return (
        <div key={variable} className='py-3'>
          <div className='py-2 text-sm text-gray-900'>
            {label[language]}
            {
              required && (
                <span className='ml-1 text-red-500'>*</span>
              )
            }
          </div>
          <Input
            className={`${disabed && 'cursor-not-allowed opacity-60'}`}
            value={value[variable] as string}
            onChange={val => handleFormChange(variable, val)}
            validated={validatedSuccess}
            placeholder={placeholder?.[language]}
            disabled={disabed}
          />
          {validating && changeKey === variable && <ValidatingTip />}
        </div>
      )
    }

    if (formSchema.type === FormTypeEnum.radio) {
      const {
        options,
        variable,
        label,
        show_on,
        required,
      } = formSchema as CredentialFormSchemaRadio

      if (show_on.length && !show_on.every(showOnItem => value[showOnItem.variable] === showOnItem.value))
        return null

      const disabed = isEditMode && (variable === '__model_type' || variable === '__model_name')

      return (
        <div key={variable} className='py-3'>
          <div className='py-2 text-sm text-gray-900'>
            {label[language]}
            {
              required && (
                <span className='ml-1 text-red-500'>*</span>
              )
            }
          </div>
          <div className={`grid grid-cols-${options?.length} gap-3`}>
            {
              options.filter((option) => {
                if (option.show_on.length)
                  return option.show_on.every(showOnItem => value[showOnItem.variable] === showOnItem.value)

                return true
              }).map(option => (
                <div
                  className={`
                    flex items-center px-3 py-2 rounded-lg border border-gray-100 bg-gray-25 cursor-pointer
                    ${value[variable] === option.value && 'bg-white border-[1.5px] border-primary-400 shadow-sm'}
                    ${disabed && '!cursor-not-allowed opacity-60'}
                  `}
                  onClick={() => handleFormChange(variable, option.value)}
                  key={`${variable}-${option.value}`}
                >
                  <div className={`
                    flex justify-center items-center mr-2 w-4 h-4 border border-gray-300 rounded-full
                    ${value[variable] === option.value && 'border-[5px] border-primary-600'}
                  `} />
                  <div className='text-sm text-gray-900'>{option.label[language]}</div>
                </div>
              ))
            }
          </div>
          {validating && changeKey === variable && <ValidatingTip />}
        </div>
      )
    }

    if (formSchema.type === 'select') {
      const {
        options,
        variable,
        label,
        show_on,
        required,
        placeholder,
      } = formSchema as CredentialFormSchemaSelect

      if (show_on.length && !show_on.every(showOnItem => value[showOnItem.variable] === showOnItem.value))
        return null

      return (
        <div key={variable} className='py-3'>
          <div className='py-2 text-sm text-gray-900'>
            {label[language]}
            {
              required && (
                <span className='ml-1 text-red-500'>*</span>
              )
            }
          </div>
          <SimpleSelect
            defaultValue={value[variable] as string}
            items={options.filter((option) => {
              if (option.show_on.length)
                return option.show_on.every(showOnItem => value[showOnItem.variable] === showOnItem.value)

              return true
            }).map(option => ({ value: option.value, name: option.label[language] }))}
            onSelect={item => handleFormChange(variable, item.value as string)}
            placeholder={placeholder?.[language]}
          />
          {validating && changeKey === variable && <ValidatingTip />}
        </div>
      )
    }
  }

  return (
    <div>
      {
        formSchemas.map(formSchema => renderField(formSchema))
      }
    </div>
  )
}

export default Form
